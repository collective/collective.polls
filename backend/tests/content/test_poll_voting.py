"""Voting, ported one to one from the legacy ``VotingTest``.

``p1`` is private, ``p2`` is open but closed to anonymous votes, ``p3`` is
open to anonymous votes. The test user is logged in as a Member.
"""

from AccessControl import Unauthorized
from collective.polls.config import PERMISSION_VOTE
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import pytest


def _active_roles(poll, permission: str) -> list[str]:
    return [r["name"] for r in poll.rolesOfPermission(permission) if r["selected"]]


WORKFLOW_ROLES = [
    "Contributor",
    "Editor",
    "Manager",
    "Member",
    "Reader",
    "Reviewer",
    "Site Administrator",
]


class TestVotePermission:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, polls) -> None:
        self.portal = portal
        self.wt = api.portal.get_tool("portal_workflow")
        self.p1 = polls["p1"]
        self.p2 = polls["p2"]
        self.p3 = polls["p3"]

    def test_private_poll(self):
        assert _active_roles(self.p1, PERMISSION_VOTE) == []

    def test_pending_poll(self):
        self.wt.doActionFor(self.p1, "submit")
        assert _active_roles(self.p1, PERMISSION_VOTE) == []

    def test_open_poll(self):
        """Without ``allow_anonymous``, the workflow's roles only."""
        assert _active_roles(self.p2, PERMISSION_VOTE) == WORKFLOW_ROLES

    def test_open_poll_anon(self):
        """With ``allow_anonymous``, Anonymous too."""
        assert _active_roles(self.p3, PERMISSION_VOTE) == [
            "Anonymous",
            *WORKFLOW_ROLES,
        ]

    def test_closed_poll(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.wt.doActionFor(self.p3, "close")
        assert _active_roles(self.p3, PERMISSION_VOTE) == []


class TestVoting:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, polls, http_request) -> None:
        self.portal = portal
        self.request = http_request
        self.wt = api.portal.get_tool("portal_workflow")
        self.p1 = polls["p1"]
        self.p2 = polls["p2"]
        self.p3 = polls["p3"]

    def test_vote_closed_poll(self):
        with pytest.raises(Unauthorized):
            self.p1.setVote(2)
        assert self.p1.getResults() == []
        assert self.p1.total_votes == 0

    def test_vote_open_poll(self):
        assert self.p2.setVote(2) is True
        assert self.p2.getResults()[2][1] == 1
        assert self.p2.total_votes == 1

    def test_vote_open_poll_reject_vote_again(self):
        setRoles(self.portal, TEST_USER_ID, ["Member", "Reviewer"])
        self.p2.setVote(2)
        assert self.p2.total_votes == 1
        # Sending the poll back erases the votes
        self.wt.doActionFor(self.p2, "reject")
        assert self.p2.total_votes == 0
        self.wt.doActionFor(self.p2, "open")
        # The user may vote again
        self.p2.setVote(2)
        assert self.p2.total_votes == 1

    def test_vote_same_user_twice(self):
        assert self.p2.setVote(2) is True
        with pytest.raises(Unauthorized):
            self.p2.setVote(2)
        assert self.p2.getResults()[2][1] == 1
        assert self.p2.total_votes == 1

    def test_vote_same_user_in_private_poll(self):
        """The legacy test voted in p1 the second time: still refused."""
        self.p2.setVote(2)
        with pytest.raises(Unauthorized):
            self.p1.setVote(2)

    @pytest.mark.parametrize(
        "option", [5, -1, None, "1", True, [], [1, 1], [1, 2], [5]], ids=repr
    )
    def test_invalid_option(self, option):
        """``[1, 2]`` is one option too many: polls are single choice by default."""
        assert self.p2.setVote(option) is False
        assert self.p2.total_votes == 0
        assert self.p2.voters() == []

    def test_list_of_one(self):
        assert self.p2.setVote([1]) is True
        assert self.p2.getResults()[1][1] == 1

    def test_anonymous_closed_poll(self):
        logout()
        with pytest.raises(Unauthorized):
            self.p1.setVote(1)
        assert self.p1.getResults() == []
        assert self.p1.total_votes == 0

    def test_anonymous_open_restricted_poll(self):
        logout()
        with pytest.raises(Unauthorized):
            self.p2.setVote(1, self.request)
        assert self.p2.getResults() == []
        assert self.p2.total_votes == 0

    def test_anonymous_open_poll(self):
        logout()
        assert self.p3.setVote(1, self.request) is True
        assert self.p3.getResults()[1][1] == 1
        assert self.p3.total_votes == 1

    def test_anonymous_open_poll_without_request(self):
        """No request, no way to recognize the voter: refused."""
        logout()
        with pytest.raises(Unauthorized):
            self.p3.setVote(1)
        assert self.p3.total_votes == 0

    def test_anonymous_twice_open_poll(self, set_request_cookies):
        logout()
        assert self.p3.setVote(1, self.request) is True
        set_request_cookies(self.request)
        with pytest.raises(Unauthorized):
            self.p3.setVote(1, self.request)
        assert self.p3.getResults()[1][1] == 1
        assert self.p3.total_votes == 1

    def test_anonymous_vote_after_reopen_poll(self, set_request_cookies, as_manager):
        logout()
        assert self.p3.setVote(1, self.request) is True
        set_request_cookies(self.request)
        as_manager(self.p3, "reject")
        as_manager(self.p3, "open")
        # The anonymous user can vote again
        assert self.p3.setVote(1, self.request) is True

    def test_anonymous_vote_sets_cookie(self):
        logout()
        self.p3.setVote(1, self.request)
        cookie_name = f"collective.poll.{self.p3.UID()}"
        cookie = self.request.response.cookies[cookie_name]
        assert cookie["Path"] == "/"
        assert f"Anonymous-{cookie['value']}" in self.p3.voters()

    def test_percentage_vote_report(self):
        poll = self.p3
        # Vote as the logged in user
        assert poll.setVote(2, self.request) is True
        assert poll.total_votes == 1
        results = poll.getResults()
        assert results[2][1] == 1
        assert results[2][2] == 1.0
        logout()
        assert poll.setVote(1, self.request) is True
        assert poll.total_votes == 2
        results = poll.getResults()
        assert results[1][1] == 1
        assert results[1][2] == 0.5

    def test_results_shape(self):
        """``(description, votes, fraction)`` per option, in option order."""
        self.p2.setVote(0)
        assert self.p2.getResults() == [
            ("Option 1", 1, 1.0),
            ("Option 2", 0, 0.0),
            ("Option 3", 0, 0.0),
        ]

    def test_modification_time(self):
        poll = self.p3
        logout()
        # a vote must modify the poll
        last_modified = poll.modified()
        poll.setVote(0, self.request)
        assert poll.modified() > last_modified
        # another vote also modifies the poll (no cookie sent back)
        last_modified = poll.modified()
        poll.setVote(0, self.request)
        assert poll.modified() > last_modified


class TestMultipleChoice:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, polls, http_request) -> None:
        self.request = http_request
        self.poll = polls["p3"]
        self.poll.max_choices = 2

    def test_multiple_choice(self):
        assert self.poll.multiple_choice is True

    def test_vote_two(self):
        assert self.poll.setVote([0, 2], self.request) is True
        assert self.poll.total_votes == 1
        assert self.poll.getResults() == [
            ("Option 1", 1, 1.0),
            ("Option 2", 0, 0.0),
            ("Option 3", 1, 1.0),
        ]

    def test_share_of_voters(self):
        """Fractions are of voters, so they can add up past 1."""
        self.poll.setVote([0, 2], self.request)
        logout()
        self.poll.setVote([0], self.request)
        assert self.poll.total_votes == 2
        assert [fraction for _, _, fraction in self.poll.getResults()] == [
            1.0,
            0.0,
            0.5,
        ]

    @pytest.mark.parametrize("option", [[0, 1, 2], [0, 0], [], [0, 9]], ids=repr)
    def test_invalid(self, option):
        assert self.poll.setVote(option, self.request) is False
        assert self.poll.voters() == []
