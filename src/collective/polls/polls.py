# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.polls.config import COOKIE_KEY
from plone import api
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletRetriever
from Products.Five.browser import BrowserView
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import random
import time


class IPolls(Interface):

    """Interface for poll utility."""

    def recent_polls(show_all=False, limit=5, kw={}):
        """Return recent polls."""

    def poll_by_uid(uid):
        """Return the poll for the given uid."""

    def voters_in_a_poll(poll):
        """Return the list of voters in a poll."""

    def voted_in_a_poll(poll):
        """Check if current user already voted."""

    def allowed_to_edit(poll):
        """Return True if member is allowed to edit a poll."""

    def allowed_to_view(poll):
        """Return True if user is allowed to view this poll."""

    def allowed_to_vote(poll):
        """Return True is user is allowed to vote in a poll."""

    def anonymous_vote_id(poll_uid):
        """Return a identifier for vote_id."""


@implementer(IPolls)
class Polls(object):

    """Utility methods for dealing with polls."""

    @property
    def ct(self):
        return api.portal.get_tool(name='portal_catalog')

    @property
    def mt(self):
        return api.portal.get_tool(name='portal_membership')

    @property
    def wt(self):
        return api.portal.get_tool(name='portal_workflow')

    @property
    def member(self):
        return self.mt.getAuthenticatedMember()

    def _query_for_polls(self, **kw):
        """Use Portal Catalog to return a list of polls."""
        kw['portal_type'] = 'collective.polls.poll'
        results = self.ct.searchResults(**kw)
        return results

    def recent_polls(self, context=None, show_all=False, limit=5, **kw):
        """Return recent polls."""
        if context is not None:
            kw['path'] = '/'.join(context.getPhysicalPath())

        kw['sort_on'] = 'created'
        kw['sort_order'] = 'reverse'
        kw['sort_limit'] = limit
        if not show_all:
            kw['review_state'] = 'open'
        results = self._query_for_polls(**kw)
        return results[:limit]

    def poll_by_uid(self, uid, context=None):
        """Return the poll for the given uid."""
        if uid == 'latest':
            results = self.recent_polls(context=context, show_all=False, limit=1)
        else:
            kw = {'UID': uid}
            results = self._query_for_polls(**kw)
        if results:
            poll = results[0].getObject()
            return poll

    def voted_in_a_poll(self, poll, request=None):
        """Check if current user already voted."""
        anonymous_allowed = poll.allow_anonymous
        member = self.member
        member_id = member.getId()
        voters = poll.voters()
        if member_id:
            return member_id in voters
        elif anonymous_allowed and request:
            cookie = COOKIE_KEY + api.content.get_uuid(poll)
            value = request.cookies.get(cookie, '')
            if value:
                value = 'Anonymous-' + value in voters
            return value
        else:
            # If we cannot be sure, we will block this user from voting again
            return True

    def allowed_to_edit(self, poll):
        """Return True if member is allowed to edit a poll."""
        return self.mt.checkPermission('Modify portal content', poll) == 1

    def allowed_to_view(self, poll):
        """Return True if user is allowed to view this poll."""
        return self.mt.checkPermission('View', poll) == 1

    def allowed_to_vote(self, poll, request=None):
        """Return True is user is allowed to vote in a poll."""
        canVote = self.mt.checkPermission('collective.polls: Vote', poll) == 1
        if canVote:
            # User must view the poll
            # and poll must be open to allow votes
            if not self.voted_in_a_poll(poll, request):
                # If user did not vote here, we allow him to vote
                return True
        # All other cases shall not pass
        raise Unauthorized

    def anonymous_vote_id(self):
        """Return a identifier for vote_id."""
        vote_id = int(time.time() * 10000000) + random.randint(0, 99)
        return vote_id


# TODO: move to browser module
class PollPortletRender(BrowserView):

    """This methods allow to use the portlet render in a view."""

    def get_portlet_manager(self, column=''):
        """Return one of default Plone portlet managers.

        @param column: "plone.leftcolumn" or "plone.rightcolumn"

        @return: plone.portlets.interfaces.IPortletManagerRenderer instance
        """
        if column:
            try:
                manager = getUtility(IPortletManager, name=column)
            except ComponentLookupError:
                # Happens when using polls in a panel from collective.panels
                manager = None
        else:
            manager = getUtility(IPortletManager, name='plone.rightcolumn')
            if not manager:
                manager = getUtility(IPortletManager, name='plone.leftcolumn')
        return manager

    def render_portlet(self, context, request, view, manager, interface):
        """Render a portlet defined in external location.

        .. note ::

            Portlets can be idenfied by id (not user visible)
            or interface (portlet class). This method supports look up
            by interface and will return the first matching portlet with
            this interface.

        @param context: Content item reference where portlet appear

        @param manager: IPortletManagerRenderer instance

        @param view: Current view or None if not available

        @param interface: Marker interface class we use to identify
            the portlet. E.g. IFacebookPortlet

        @return: Rendered portlet HTML as a string, or empty string if
            portlet not found
        """
        if manager is None:
            return ''

        retriever = getMultiAdapter((context, manager), IPortletRetriever)

        portlets = retriever.getPortlets()

        assignment = None

        for portlet in portlets:

            # portlet is {'category': 'context',
            # 'assignment': <FacebookLikeBoxAssignment at facebook-like-box>,
            # 'name': u'facebook-like-box',
            # 'key': '/isleofback/sisalto/huvit-ja-harrasteet
            # Identify portlet by interface provided by assignment
            if interface.providedBy(portlet['assignment']):
                assignment = portlet['assignment']
                break

        if assignment is None:
            # Did not find a portlet
            return ''

        # - A special type of content provider, IPortletRenderer, knows how to
        # render each type of portlet. The IPortletRenderer should be a
        # multi-adapter from (context, request, view, portlet manager,
        #                     data provider).

        renderer = queryMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer
        )

        # Make sure we have working acquisition chain
        renderer = renderer.__of__(context)

        if renderer is None:
            raise RuntimeError(
                'No portlet renderer found for portlet assignment: ' + str(assignment))

        renderer.update()
        # Does not check visibility here... force render always
        html = renderer.render()

        return html

    def render(self):
        """Render a portlet from another page in-line to this page.

        Does not render other portlets in the same portlet manager.
        """
        context = self.context.aq_inner
        request = self.request
        view = self

        # Alternatively, you can directly query your custom portlet manager
        # by interface
        from collective.polls.portlet.voteportlet import IVotePortlet
        column = self.request['column'] if 'column' in self.request else ''
        manager = self.get_portlet_manager(column)

        html = self.render_portlet(context, request, view,
                                   manager, IVotePortlet)
        return html
