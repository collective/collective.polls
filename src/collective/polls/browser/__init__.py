# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.polls.polls import IPolls
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
        utility = self.utility
        poll = self.poll()
        if poll:
            can_view = utility.allowed_to_view(poll)
            # Do not show this portlet in the poll context
            return can_view and not (poll == self.context)
        return False

    def poll_uid(self):
        """Return uid for current poll."""
        utility = self.utility
        return utility.uid_for_poll(self.poll())

    @property
    def can_vote(self):
        if hasattr(self, '_has_voted') and self._has_voted:
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
        utility = self.utility
        return utility.allowed_to_edit(self.context)

    def is_closed(self):
        state = 'closed'
        if self.poll():
            state = self.context.portal_workflow.getInfoFor(
                self.poll(), 'review_state')
        return state == 'closed'

    @property
    def has_voted(self):
        """Return True if the current user voted in this poll."""
        if hasattr(self, '_has_voted') and self._has_voted:
            return True
        utility = self.utility
        voted = utility.voted_in_a_poll(self.context, self.request)
        return voted

    def voting_results(self):
        poll = self.poll()
        if poll and poll.show_results:
            return poll.getResults()
        return None
