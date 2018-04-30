# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.polls.config import COOKIE_KEY
from plone import api
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
    def mt(self):
        return api.portal.get_tool(name='portal_membership')

    @property
    def member(self):
        return self.mt.getAuthenticatedMember()

    def recent_polls(self, context=None, show_all=False, limit=5, **kw):
        """Return recent polls."""
        if context is not None:
            kw['path'] = '/'.join(context.getPhysicalPath())

        kw['portal_type'] = 'collective.polls.poll'
        kw['sort_on'] = 'created'
        kw['sort_order'] = 'reverse'
        kw['sort_limit'] = limit
        if not show_all:
            kw['review_state'] = 'open'

        results = api.content.find(**kw)
        return results[:limit]

    def poll_by_uid(self, uid, context=None):
        """Return the poll for the given uid."""
        if uid == 'latest':
            results = self.recent_polls(context=context, show_all=False, limit=1)
        else:
            results = api.content.find(UID=uid)
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
