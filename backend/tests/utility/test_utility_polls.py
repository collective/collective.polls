"""``IPolls``: finding polls and permission checks.

Six polls: p1, p2, p3 in a published folder, p4, p5, p6 in a published
subfolder. p2 and p5 are open; the others stay private.
"""

from . import PORTAL_TYPE
from . import UTILITY_NAME
from AccessControl import Unauthorized
from collective.polls.utility import IPolls
from plone import api
from plone.app.testing import logout
from plone.uuid.interfaces import IUUID
from zope.component import getUtility

import pytest


class TestUtility:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, http_request) -> None:
        self.portal = portal
        self.request = http_request
        self.utility = getUtility(IPolls, name=UTILITY_NAME)
        with api.env.adopt_roles(["Manager"]):
            self.folder = api.content.create(portal, "Document", "folder")
            api.content.transition(obj=self.folder, transition="publish")
            self.subfolder = api.content.create(self.folder, "Document", "folder")
            api.content.transition(obj=self.subfolder, transition="publish")
            for poll_id in ("p1", "p2", "p3"):
                self.folder.invokeFactory(PORTAL_TYPE, poll_id)
            for poll_id in ("p4", "p5", "p6"):
                self.subfolder.invokeFactory(PORTAL_TYPE, poll_id)
            api.content.transition(obj=self.folder["p2"], transition="open")
            api.content.transition(obj=self.subfolder["p5"], transition="open")

    def test_utility_registered(self):
        assert IPolls.providedBy(self.utility)

    def test_recent_polls(self):
        """Five recent polls, including closed ones."""
        assert len(self.utility.recent_polls(show_all=True)) == 5

    def test_recent_polls_expand_limit(self):
        assert len(self.utility.recent_polls(show_all=True, limit=10)) == 6

    def test_open_recent_polls(self):
        assert len(self.utility.recent_polls(show_all=False)) == 2

    def test_recent_polls_newest_first(self):
        brains = self.utility.recent_polls(show_all=True, limit=10)
        created = [brain.created for brain in brains]
        assert created == sorted(created, reverse=True)

    def test_polls_context(self):
        polls = self.utility.recent_polls(context=self.subfolder, show_all=True)
        assert len(polls) == 3

    def test_open_polls_context(self):
        polls = self.utility.recent_polls(context=self.subfolder, show_all=False)
        assert len(polls) == 1

    def test_recent_polls_extra_query(self):
        polls = self.utility.recent_polls(show_all=True, review_state="private")
        assert len(polls) == 4

    def test_poll_by_uid(self):
        base_poll = self.subfolder["p5"]
        assert self.utility.poll_by_uid(uid=IUUID(base_poll)) == base_poll

    def test_poll_by_uid_unknown(self):
        assert self.utility.poll_by_uid(uid="not-a-uid") is None

    def test_latest_poll(self):
        assert self.utility.poll_by_uid(uid="latest") == self.subfolder["p5"]

    def test_latest_poll_in_context(self):
        poll = self.utility.poll_by_uid(uid="latest", context=self.folder["p1"])
        assert poll is None

    def test_voted_in_a_poll(self):
        poll = self.subfolder["p5"]
        poll.options = [{"option_id": 0, "description": "Option 1"}]
        assert self.utility.voted_in_a_poll(poll) is False
        poll.setVote(0)
        assert self.utility.voted_in_a_poll(poll) is True

    def test_error_voted_in_a_poll(self):
        """Anonymous, and no request to read a cookie from: assume voted."""
        logout()
        assert self.utility.voted_in_a_poll(self.subfolder["p5"]) is True

    def test_anonymous_not_allowed_counts_as_voted(self):
        """Anonymous on a poll closed to anonymous votes: assume voted."""
        poll = self.subfolder["p5"]
        poll.allow_anonymous = False
        logout()
        assert self.utility.voted_in_a_poll(poll, self.request) is True

    def test_anonymous_without_cookie(self):
        logout()
        assert self.utility.voted_in_a_poll(self.subfolder["p5"], self.request) is False

    def test_anonymous_with_unknown_cookie(self):
        poll = self.subfolder["p5"]
        self.request.cookies[f"collective.poll.{poll.UID()}"] = "made-up"
        logout()
        assert self.utility.voted_in_a_poll(poll, self.request) is False

    def test_allowed_to_vote(self):
        assert self.utility.allowed_to_vote(self.subfolder["p5"]) is True
        with pytest.raises(Unauthorized):
            self.utility.allowed_to_vote(self.subfolder["p6"])

    def test_allowed_to_view(self):
        assert self.utility.allowed_to_view(self.subfolder["p5"]) is True

    def test_allowed_to_edit(self):
        """The owner may edit a private poll."""
        assert self.utility.allowed_to_edit(self.subfolder["p6"]) is True

    def test_not_allowed_to_edit(self):
        """Nobody may edit an open poll."""
        assert self.utility.allowed_to_edit(self.subfolder["p5"]) is False

    def test_anonymous_allowed_to_view(self):
        logout()
        assert self.utility.allowed_to_view(self.subfolder["p5"]) is True

    def test_anonymous_not_allowed_to_view(self):
        logout()
        assert self.utility.allowed_to_view(self.subfolder["p6"]) is False

    def test_anonymous_vote_id(self):
        first = self.utility.anonymous_vote_id()
        second = self.utility.anonymous_vote_id()
        assert isinstance(first, str)
        assert len(first) >= 16
        assert first != second
