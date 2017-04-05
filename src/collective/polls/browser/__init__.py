# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.polls.polls import IPolls
from plone import api
from zope.component import queryUtility


class PollsViewMixin:

    """Common methods and functions used by views, tiles and portlets."""

    @property
    def utility(self):
        """Access to IPolls utility."""
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    @property
    def available(self):
        """Check if Poll is available."""
        utility = self.utility
        poll = self.poll()
        if poll:
            can_view = utility.allowed_to_view(poll)
            # Do not show this portlet in the poll context
            return can_view and not (poll == self.context)
        return False

    def poll_uid(self):
        """Return UUID for current poll."""
        return api.content.get_uuid(self.poll())

    @property
    def can_vote(self):
        """Check if user can vote."""
        if getattr(self, '_has_voted', False) and self._has_voted:
            # This is mainly to avoid anonymous users seeing the form again
            return False
        utility = self.utility
        poll = self.poll()
        if poll:
            try:
                return utility.allowed_to_vote(poll, self.request)
            except Unauthorized:
                return False
        return False

    @property
    def can_edit(self):
        """Check if user can edit the poll."""
        utility = self.utility
        poll = self.poll()
        return utility.allowed_to_edit(poll)

    def is_closed(self):
        """Check if poll is closed."""
        state = 'closed'
        poll = self.poll()
        if poll:
            state = poll.portal_workflow.getInfoFor(
                poll, 'review_state')
        return state == 'closed'

    @property
    def has_voted(self):
        """Return True if the current user voted in this poll."""
        if getattr(self, '_has_voted', False) and self._has_voted:
            return True
        poll = self.poll()
        utility = self.utility
        voted = utility.voted_in_a_poll(poll, self.request)
        return voted

    def voting_results(self):
        """Get the voting results."""
        poll = self.poll()
        if poll and poll.show_results:
            return poll.getResults()
        return None

    @property
    def total_votes(self):
        """Return the number of votes so far."""
        poll = self.poll()
        return poll.total_votes
