"""What happens to a poll when it is opened, rejected, or moved otherwise."""

from . import PERMISSION_VOTE
from collective.polls.subscribers.workflow import grant_anonymous_vote
from plone.app.testing import logout

import pytest


def _anonymous_can_vote(poll) -> bool:
    roles = [
        r["name"] for r in poll.rolesOfPermission(PERMISSION_VOTE) if r["selected"]
    ]
    return "Anonymous" in roles


class TestOpen:
    @pytest.mark.parametrize(
        "where,allow_anonymous,expected",
        [
            ("root", True, True),
            (None, True, True),
            ("private", True, False),
            ("root", False, False),
            (None, False, False),
        ],
    )
    def test_anonymous_grant(
        self, make_poll, transition, where, allow_anonymous, expected
    ):
        """Anonymous may vote only when allowed and the parent is visible."""
        poll = make_poll(where, allow_anonymous)
        transition(poll, "open")
        assert _anonymous_can_vote(poll) is expected

    def test_grant_returns_result(self, make_poll):
        """The helper reports whether it granted the permission."""
        assert grant_anonymous_vote(make_poll("root", True)) is True

    def test_grant_refused_returns_false(self, make_poll):
        assert grant_anonymous_vote(make_poll("private", True)) is False

    def test_other_transitions_grant_nothing(self, make_poll, transition):
        poll = make_poll(None, True)
        transition(poll, "submit")
        assert _anonymous_can_vote(poll) is False


class TestReject:
    def test_clears_votes(self, make_poll, transition, http_request):
        poll = make_poll(None, True)
        transition(poll, "open")
        poll.setVote(0)
        logout()
        poll.setVote(1, http_request)
        assert poll.total_votes == 2
        transition(poll, "reject")
        assert poll.total_votes == 0
        assert poll.voters() == []
        assert poll.getResults() == []

    @pytest.mark.parametrize("transitions", [["close"], ["close", "open"]])
    def test_other_transitions_keep_votes(self, make_poll, transition, transitions):
        poll = make_poll(None, True)
        transition(poll, "open")
        poll.setVote(0)
        for transition_id in transitions:
            transition(poll, transition_id)
        assert poll.total_votes == 1
        assert len(poll.voters()) == 1
