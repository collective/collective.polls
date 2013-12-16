# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.polls import MessageFactory as _
from collective.polls.polls import IPolls
from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.component import queryUtility
from zope.formlib import form
from zope.interface import alsoProvides
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def PossiblePolls(context):
    portal_state = api.content.get_view(
        name='plone_portal_state',
        context=context,
        request=context.REQUEST
    )
    utility = queryUtility(IPolls, name='collective.polls')
    navigation_root = portal_state.navigation_root()
    polls = utility.recent_polls(context=navigation_root, show_all=False, limit=999999)

    values = [SimpleTerm(value="latest", title=_(u"Latest opened poll"))]
    values.extend(
        SimpleTerm(value=i.UID, title=i.Title.decode('utf-8'))
        for i in polls
    )

    return SimpleVocabulary(values)


alsoProvides(PossiblePolls, IContextSourceBinder)


class IVotePortlet(IPortletDataProvider):
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u'Header'),
        description=_(u"The header for the portlet. Leave empty for none."),
        required=False,
    )

    poll = schema.Choice(
        title=_(u'Poll'),
        description=_(u"Which poll to show in the portlet."),
        required=True,
        source=PossiblePolls,
    )

    show_total = schema.Bool(
        title=_(u'Show total votes'),
        description=_(u'Show the number of collected votes so far.'),
        default=True,
    )

    show_closed = schema.Bool(
        title=_(u'Show closed polls'),
        description=_(
            u"If there is no available open poll or the chosen poll is "
            u"already closed, should the porlet show the results instead."),
        default=False,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IVotePortlet)

    header = u""
    poll = None

    def __init__(self, poll, header=u"", show_total=True, show_closed=False):
        self.header = header
        self.poll = poll
        self.show_total = show_total
        self.show_closed = show_closed

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Voting portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('voteportlet.pt')

    @property
    def utility(self):
        """ Access to IPolls utility
        """
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    def getHeader(self):
        """ Returns the header for the portlet
        """
        return self.data.header

    def portlet_manager_name(self):
        column = self.manager.__name__
        # Check that we can reach this manager.  If this does not
        # work, we cannot refresh the portlet.  This happens when
        # using polls in a panel from collective.panels and possibly
        # in other situations.  We will not activate the ajax portlet
        # refresh then.
        try:
            getUtility(IPortletManager, name=column)
        except ComponentLookupError:
            return ''
        return column

    @memoize
    def poll(self):
        portal_state = api.content.get_view(
            name='plone_portal_state',
            context=self.context,
            request=self.context.REQUEST
        )
        navigation_root = portal_state.navigation_root()
        utility = self.utility
        uid = self.data.poll
        poll = utility.poll_by_uid(uid, context=navigation_root)
        if not poll and self.data.show_closed:
            # if we have no open poll, try closed ones
            results = utility.recent_polls(
                context=navigation_root,
                show_all=True,
                limit=1,
                review_state='closed'
            )
            poll = results and results[0].getObject() or None
        return poll

    def poll_uid(self):
        """ Return uid for current poll
        """
        utility = self.utility
        return utility.uid_for_poll(self.poll())

    def getVotingResults(self):
        poll = self.poll()
        if poll.show_results:
            return poll.getResults()
        else:
            return None

    @property
    def can_vote(self):
        utility = self.utility
        poll = self.poll()
        try:
            return utility.allowed_to_vote(poll, self.request)
        except Unauthorized:
            return False

    @property
    def available(self):
        utility = self.utility
        poll = self.poll()
        if poll:
            can_view = utility.allowed_to_view(poll)
            # Do not show this portlet in the poll context
            return can_view and not (poll == self.context)
        return False

    def is_closed(self):
        state = self.context.portal_workflow.getInfoFor(
            self.poll(), 'review_state')
        return state == 'closed'

    def show_total(self):
        return getattr(self.data, 'show_total', True)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IVotePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.

    For field added to the interface in version 1.5.dev0, instead of creating
    an upgrade step that should iterate over all objects of the site, we add
    a check in the __call__ method

    These new field has an explicit default_value.
    """
    form_fields = form.Fields(IVotePortlet)

    def __call__(self):
        new_fields = ('show_total', )
        for new_field in new_fields:
            if not hasattr(self.context, new_field):
                field = self.form_fields.get(new_field)
                setattr(self.context, new_field, field.field.default)
        return super(EditForm, self).__call__()
