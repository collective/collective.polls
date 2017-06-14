# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.polls import MessageFactory as _
from collective.polls.browser import PollsViewMixin
from collective.polls.config import COOKIE_KEY
from collective.polls.config import MEMBERS_ANNO_KEY
from collective.polls.config import PERMISSION_VOTE
from collective.polls.config import VOTE_ANNO_KEY
from collective.polls.polls import IPolls
from collective.polls.widgets.enhancedtextlines import EnhancedTextLinesFieldWidget
from plone import api
from plone.autoform import directives as form
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.content import Item
from plone.supermodel import model
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


graph_options = SimpleVocabulary(
    [SimpleTerm(value=u'bar', title=_(u'Bar Chart')),
     SimpleTerm(value=u'pie', title=_(u'Pie Chart')),
     SimpleTerm(value=u'numbers', title=_(u'Numbers Only'))])


class InsuficientOptions(Invalid):
    __doc__ = _(u'Not enought options provided')


# TODO: move to interfaces module
class IPoll(model.Schema):

    """A Poll in a Plone site."""

    allow_anonymous = schema.Bool(
        title=_(u'Allow anonymous'),
        description=_(
            u'Allow not logged in users to vote. '
            u'The parent folder of this poll should be published before opeining the poll for this field to take effect'),
        default=True,
    )

    # multivalue = schema.Bool(
    #    title = _(u"Multivalue"),
    #    description = _(u"Voters can choose several answers at the same "
    #                     "time."),
    # )

    show_results = schema.Bool(
        title=_(u'Show partial results'),
        description=_(
            u'Show partial results after a voter has already voted.'),
        default=True,
    )

    results_graph = schema.Choice(
        title=_(u'Graph'),
        description=_(u'Format to show the results.'),
        default='bar',
        required=True,
        source=graph_options,
    )

    form.widget(options=EnhancedTextLinesFieldWidget)
    options = schema.List(
        title=_(u'Available options'),
        value_type=schema.TextLine(),
        default=[],
        required=True,
    )

    @invariant
    def validate_options(data):
        """Validate options."""
        options = data.options
        descriptions = options and [o for o in options]
        if len(descriptions) < 2:
            raise InsuficientOptions(
                _(u'You need to provide at least two options for a poll.'))


@implementer(IPoll)
class Poll(Item):

    """A Poll in a Plone site."""

    __ac_permissions__ = (
        (PERMISSION_VOTE, ('setVote', '_setVoter', )),
    )

    @property
    def annotations(self):
        return IAnnotations(self)

    @property
    def utility(self):
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    def getOptions(self):
        """Return available options."""
        options = self.options
        return options

    def _getVotes(self):
        """Return votes in a dict format."""
        votes = {'options': [],
                 'total': 0}
        for option in self.getOptions():
            index = option.get('option_id')
            description = option.get('description')
            option_votes = self.annotations.get(VOTE_ANNO_KEY % index, 0)  # noqa: S001
            votes['options'].append({'description': description,
                                     'votes': option_votes,
                                     'percentage': 0.0})
            votes['total'] = votes['total'] + option_votes
        for option in votes['options']:
            if option['votes']:
                option['percentage'] = option['votes'] / float(votes['total'])
        return votes

    def getResults(self):
        """Return results so far."""
        votes = self._getVotes()
        # Bars show wrong when there are no vote
        if votes['total'] == 0:
            return []
        all_results = []
        for item in votes['options']:
            all_results.append((item['description'],
                                item['votes'],
                                item['percentage']))
        return all_results

    def _validateVote(self, options=[]):
        """Check if passed options are available here."""
        available_options = [o['option_id'] for o in self.getOptions()]
        if isinstance(options, list):
            # TODO: Allow multiple options
            # multivalue = self.multivalue
            return False
        else:
            return options in available_options

    def _setVoter(self, request=None):
        """Mark this user as a voter."""
        utility = self.utility
        annotations = self.annotations
        voters = self.voters()
        member = utility.member
        member_id = member.getId()
        if not member_id and request:
            cookie = COOKIE_KEY + api.content.get_uuid(self)
            expires = 'Wed, 19 Feb 2020 14:28:00 GMT'  # XXX: why hardcoded?
            vote_id = str(utility.anonymous_vote_id())
            request.response[cookie] = vote_id
            request.response.setCookie(cookie,
                                       vote_id,
                                       path='/',
                                       expires=expires)
            member_id = 'Anonymous-' + vote_id

        if member_id:
            voters.append(member_id)
            annotations[MEMBERS_ANNO_KEY] = voters
            return True

    def voters(self):
        annotations = self.annotations
        voters = annotations.get(MEMBERS_ANNO_KEY, [])
        return voters

    @property
    def total_votes(self):
        """Return the number of votes so far."""
        votes = self._getVotes()
        return votes['total']

    def setVote(self, options=[], request=None):
        """Set a vote on this poll."""
        annotations = self.annotations
        utility = self.utility
        try:
            if not utility.allowed_to_vote(self, request):
                return False
        except Unauthorized:
            raise Unauthorized
        if not self._validateVote(options):
            return False
        if not isinstance(options, list):
            options = [options, ]
        if not self._setVoter(request):
            # We failed to set voter, so we will not compute its votes
            return False
        # set vote in annotation storage
        for option in options:
            vote_key = VOTE_ANNO_KEY % option  # noqa: S001
            votes = annotations.get(vote_key, 0)
            annotations[vote_key] = votes + 1
        return True


# TODO: move to browser module
class PollAddForm(DefaultAddForm):
    """Form to handle creation of new Polls."""

    portal_type = 'collective.polls.poll'

    def create(self, data):
        options = data['options']
        new_data = []
        for (index, option) in enumerate(options):
            option_new = {}
            option_new['option_id'] = index
            option_new['description'] = option
            new_data.append(option_new)
        data['options'] = new_data
        return super(PollAddForm, self).create(data)


# TODO: move to browser module
class PollAddView(DefaultAddView):
    form = PollAddForm


# TODO: move to browser module
class PollEditForm(DefaultEditForm):
    """Form to handle edition of existing polls."""

    def updateWidgets(self):
        """Update form widgets to hide column option_id from end user."""
        super(PollEditForm, self).updateWidgets()

        self.widgets['options'].allow_reorder = True
        data = ''
        for option in self.widgets['options'].value.split('\n'):
            if data:
                data += '\n'
            if option.strip().startswith('{'):
                new_val = eval(option)
                data += new_val['description']
            else:
                data = option
        self.widgets['options'].value = data

    def applyChanges(self, data):
        options = data['options']
        new_data = []
        for (index, option) in enumerate(options):
            option_new = {}
            option_new['option_id'] = index
            option_new['description'] = option
            new_data.append(option_new)
        data['options'] = new_data
        super(PollEditForm, self).applyChanges(data)


# TODO: move to browser module
class View(PollsViewMixin, BrowserView):

    index = ViewPageTemplateFile('templates/view.pt')

    def render(self):
        return self.index()

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        context = aq_inner(self.context)
        self.context = context
        self.state = getMultiAdapter(
            (context, self.request), name=u'plone_context_state')
        self.wf_state = self.state.workflow_state()
        # Handle vote
        form = self.request.form
        self.errors = []
        self.messages = []

        # if the poll is open and anonymous should vote but the parent folder
        # is private.. inform the user.

        # When the poll's container is the site's root, we do not need to
        # check the permissions.
        container = aq_parent(aq_inner(self.context))

        if 'open' == self.wf_state and not ISiteRoot.providedBy(container):
            roles = [
                r['name'] for r in
                self.context.rolesOfPermission('collective.polls: Vote')
                if r['selected']]

            if 'Anonymous' not in roles and self.context.allow_anonymous:
                msg = _(
                    u"Anonymous user won't be able to vote, you forgot to "
                    u'publish the parent folder, you must sent back the poll '
                    u'to private state, publish the parent folder and open '
                    u'the poll again'
                )
                api.portal.show_message(msg, self.request, type='warn')

        if 'poll.submit' in form:
            self._updateForm(form)
        # Update status messages
        for error in self.errors:
            api.portal.show_message(error, self.request, type='warn')
        for msg in self.messages:
            api.portal.show_message(msg, self.request, type='info')

        # XXX
        # if 'voting.from' in form:
        #     url = form['voting.from']
        #     self.request.RESPONSE.redirect(url)

    def _updateForm(self, form):
        INVALID_OPTION = _(u'Invalid option')
        options = form.get('options', '')
        if isinstance(options, list):
            self.errors.append(INVALID_OPTION)
        elif isinstance(options, str):
            if not options.isdigit():
                self.errors.append(INVALID_OPTION)
            else:
                options = int(options)
        if not self.errors:
            # Let's vote
            try:
                self.context.setVote(options, self.request)
                self.messages.append(_(u'Thanks for your vote'))
                # We do this to avoid redirecting anonymous user as
                # we just sent them the cookie
                self._has_voted = True
            except Unauthorized:
                self.errors.append(_(u'You are not authorized to vote'))

    def poll(self):
        return self.context

    def getOptions(self):
        """Return available options."""
        return self.context.getOptions()
