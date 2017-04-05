# -*- coding: utf-8 -*-
from collective.polls import MessageFactory as _
from collective.polls.browser import PollsViewMixin
from collective.polls.config import IS_PLONE_5
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
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


if not IS_PLONE_5:  # BBB
    from zope.formlib import form


def PossiblePolls(context):
    portal_state = api.content.get_view(
        name='plone_portal_state',
        context=context,
        request=context.REQUEST
    )
    utility = queryUtility(IPolls, name='collective.polls')
    navigation_root = portal_state.navigation_root()
    polls = utility.recent_polls(context=navigation_root, show_all=False, limit=999999)

    values = [SimpleTerm(value='latest', title=_(u'Latest opened poll'))]
    values.extend(
        SimpleTerm(value=i.UID, title=i.Title.decode('utf-8'))
        for i in polls
    )

    return SimpleVocabulary(values)


alsoProvides(PossiblePolls, IContextSourceBinder)


class IVotePortlet(IPortletDataProvider):
    """A portlet."""

    header = schema.TextLine(
        title=_(u'Header'),
        description=_(u'The header for the portlet. Leave empty for none.'),
        required=False,
    )

    poll = schema.Choice(
        title=_(u'Poll'),
        description=_(u'Which poll to show in the portlet.'),
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
            u'If there is no available open poll or the chosen poll is '
            u'already closed, should the porlet show the results instead.'),
        default=False,
    )

    link_poll = schema.Bool(
        title=_(u'Add a link to the poll'),
        description=u'',
        default=True,
    )


@implementer(IVotePortlet)
class Assignment(base.Assignment):
    """Portlet assignment."""

    poll = None
    header = u''
    show_total = True
    show_closed = True
    link_poll = True

    def __init__(self, poll=u'latest', header=u'', show_total=True, show_closed=False,
                 link_poll=True):
        self.header = header
        self.poll = poll
        self.show_total = show_total
        self.show_closed = show_closed
        self.link_poll = link_poll

    @property
    def title(self):
        """Return the title of the portlet in the 'manage portlets' screen."""
        return _(u'Voting portlet')


class Renderer(PollsViewMixin, base.Renderer):
    """Portlet renderer."""

    render = ViewPageTemplateFile('voteportlet.pt')

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


class AddForm(base.AddForm):
    """Portlet add form."""

    if IS_PLONE_5:
        schema = IVotePortlet
    else:  # BBB
        form_fields = form.Fields(IVotePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form."""

    if IS_PLONE_5:
        schema = IVotePortlet
    else:  # BBB
        form_fields = form.Fields(IVotePortlet)
