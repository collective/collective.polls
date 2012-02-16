# -*- coding:utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_inner
from five import grok

from zope import schema
from zope import interface

from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.interface import invariant, Invalid

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from z3c.form.interfaces import HIDDEN_MODE

from plone.directives import dexterity
from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from Products.statusmessages.interfaces import IStatusMessage

from collective.polls.config import COOKIE_KEY
from collective.polls.config import MEMBERS_ANNO_KEY
from collective.polls.config import VOTE_ANNO_KEY

from collective.polls.config import PERMISSION_VOTE

from collective.polls.polls import IPolls

from collective.polls.utils import anonymous_view_parent

from collective.polls import MessageFactory as _


graph_options = SimpleVocabulary(
    [SimpleTerm(value=u'bar', title=_(u'Bar Chart')),
     SimpleTerm(value=u'pie', title=_(u'Pie Chart')),
     SimpleTerm(value=u'numbers', title=_(u'Numbers Only'))])


class InsuficientOptions(Invalid):
    __doc__ = _(u"Not enought options provided")


class IOption(interface.Interface):
    ''' An option in a poll '''

    option_id = schema.Int(
        title=u"Option Id",
        required=False)

    description = schema.TextLine(
        title=_(u"Description"),
        required=True)


class IPoll(form.Schema):
    """ A Poll in a Plone site
    """

    allow_anonymous = schema.Bool(
        title=_(u"Allow anonymous"),
        description=_(u"Allow not logged in users to vote."),
        default=True,
        )

    #multivalue = schema.Bool(
        #title = _(u"Multivalue"),
        #description = _(u"Voters can choose several answers at the same "
                         #"time."),
        #)

    show_results = schema.Bool(
        title=_(u"Show partial results"),
        description=_(u"Show partial results after a voter has already "
                       "voted."),
        default=True,
        )

    results_graph = schema.Choice(
        title=_(u'Graph'),
        description=_(u"Format to show the results."),
        default='bar',
        required=True,
        source=graph_options)

    options = schema.List(
        title=_(u"Available options"),
        value_type=DictRow(title=_(u'Option'),
                           schema=IOption),
        default=[],
        required=True)

    @invariant
    def validate_options(data):
        ''' Validate options '''
        options = data.options
        descriptions = options and [o['description'].strip() for o in options]
        if len(descriptions) < 2:
            raise InsuficientOptions(
                    _(u"You need to provide at least two options for a poll."))


class Poll(dexterity.Item):
    """ A Poll in a Plone site
    """

    grok.implements(IPoll)

    __ac_permissions__ = (
        (PERMISSION_VOTE,
         ('setVote', '_setVoter', )),
        )

    @property
    def annotations(self):
        return IAnnotations(self)

    @property
    def utility(self):
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    def getOptions(self):
        ''' Returns available options '''
        options = self.options
        return options

    def _getVotes(self):
        ''' Return votes in a dict format '''
        votes = {'options': [],
                 'total': 0}
        for option in self.getOptions():
            index = option.get('option_id')
            description = option.get('description')
            option_votes = self.annotations.get(VOTE_ANNO_KEY % index, 0)
            votes['options'].append({'description': description,
                                     'votes': option_votes,
                                     'percentage': 0.0})
            votes['total'] = votes['total'] + option_votes
        for option in votes['options']:
            if option['votes']:
                option['percentage'] = option['votes'] / float(votes['total'])
        return votes

    def getResults(self):
        ''' Returns results so far '''
        votes = self._getVotes()
        all_results = []
        for item in votes['options']:
            all_results.append((item['description'],
                                item['votes'],
                                item['percentage']))
        return all_results

    def _validateVote(self, options=[]):
        ''' Check if passed options are available here '''
        available_options = [o['option_id'] for o in self.getOptions()]
        if isinstance(options, list):
            # TODO: Allow multiple options
            # multivalue = self.multivalue
            return False
        else:
            return options in available_options

    def _setVoter(self, request=None):
        ''' Mark this user as a voter '''
        utility = self.utility
        annotations = self.annotations
        voters = self.voters()
        member = utility.member
        member_id = member.getId()
        if not member_id and request:
            poll_uid = utility.uid_for_poll(self)
            cookie = COOKIE_KEY % str(poll_uid)
            expires = 'Wed, 19 Feb 2020 14:28:00 GMT'
            vote_id = str(utility.anonymous_vote_id())
            request.response[cookie] = vote_id
            request.response.setCookie(cookie,
                                       vote_id,
                                       path='/',
                                       expires=expires)
            member_id = 'Anonymous-%s' % vote_id

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
        ''' Return the # of votes so far'''
        votes = self._getVotes()
        return votes['total']

    def setVote(self, options=[], request=None):
        ''' Set a vote on this poll '''
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
            vote_key = VOTE_ANNO_KEY % option
            votes = annotations.get(vote_key, 0)
            annotations[vote_key] = votes + 1
        return True


class PollAddForm(dexterity.AddForm):
    """ Form to handle creation of new Polls
    """

    grok.name('collective.polls.poll')

    def updateFields(self):
        ''' Update form fields to set options to use DataGridFieldFactory '''
        super(PollAddForm, self).updateFields()
        self.fields['options'].widgetFactory = DataGridFieldFactory

    def datagridUpdateWidgets(self, subform, widgets, widget):
        ''' Hides the widgets in the datagrid subform '''
        widgets['option_id'].mode = HIDDEN_MODE

    def updateWidgets(self):
        ''' Update form widgets to hide column option_id from end user '''
        super(PollAddForm, self).updateWidgets()
        if not anonymous_view_parent(self.context):
            self.widgets['allow_anonymous'].mode = HIDDEN_MODE
        self.widgets['options'].allow_reorder = True
        self.widgets['options'].columns[0]['mode'] = HIDDEN_MODE

    def create(self, data):
        options = data['options']
        for (index, option) in enumerate(options):
            option['option_id'] = index
        return super(PollAddForm, self).create(data)


class PollEditForm(dexterity.EditForm):
    """ Form to handle edition of existing Polls
    """

    grok.context(IPoll)

    def updateFields(self):
        ''' Update form fields to set options to use DataGridFieldFactory '''
        super(PollEditForm, self).updateFields()
        self.fields['options'].widgetFactory = DataGridFieldFactory

    def datagridUpdateWidgets(self, subform, widgets, widget):
        ''' Hides the widgets in the datagrid subform '''
        widgets['option_id'].mode = HIDDEN_MODE

    def updateWidgets(self):
        ''' Update form widgets to hide column option_id from end user '''
        super(PollEditForm, self).updateWidgets()
        if not anonymous_view_parent(self.context):
            self.widgets['allow_anonymous'].mode = HIDDEN_MODE
        self.widgets['options'].allow_reorder = True
        self.widgets['options'].columns[0]['mode'] = HIDDEN_MODE

    def applyChanges(self, data):
        options = data['options']
        for (index, option) in enumerate(options):
            option['option_id'] = index
        super(PollEditForm, self).applyChanges(data)


class View(grok.View):

    grok.context(IPoll)
    grok.require('zope2.View')

    grok.name('view')

    def update(self):
        super(View, self).update()
        messages = IStatusMessage(self.request)
        context = aq_inner(self.context)
        self.context = context
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.wf_state = self.state.workflow_state()
        self.utility = context.utility

        # Handle vote
        form = self.request.form
        self.errors = []
        self.messages = []

        INVALID_OPTION = _(u'Invalid option')
        if 'poll.submit' in form:
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
        # Update status messages
        for error in self.errors:
            messages.addStatusMessage(error, type="warn")
        for msg in self.messages:
            messages.addStatusMessage(msg, type="info")

        if 'voting.from' in form:
            url = form['voting.from']
            #self.request.RESPONSE.redirect(url)

    @property
    def can_vote(self):
        if hasattr(self, '_has_voted') and self._has_voted:
            # This is mainly to avoid anonymous users seeing the form again
            return False
        utility = self.utility
        try:
            return utility.allowed_to_vote(self.context, self.request)
        except Unauthorized:
            return False

    @property
    def can_edit(self):
        utility = self.utility
        return utility.allowed_to_edit(self.context)

    @property
    def has_voted(self):
        ''' has the current user voted in this poll? '''
        if hasattr(self, '_has_voted') and self._has_voted:
            return True
        utility = self.utility
        voted = utility.voted_in_a_poll(self.context, self.request)
        return voted

    def poll_uid(self):
        ''' Return uid for current poll '''
        utility = self.utility
        return utility.uid_for_poll(self.context)

    def getOptions(self):
        ''' Returns available options '''
        return self.context.getOptions()

    def getResults(self):
        ''' Returns results so far if allowed'''
        show_results = False
        if self.wf_state == 'open':
            show_results = show_results or self.context.show_results
        elif self.wf_state == 'closed':
            show_results = True
        return (show_results and self.context.getResults()) or None
