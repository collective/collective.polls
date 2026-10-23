"""The closing date: when voting ends without anyone closing the poll.

``p2`` is open but closed to anonymous votes; the test user is logged in
as a Member.
"""

from collective.polls.content.poll import IPoll
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import PollClosed
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest


PAST = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
FUTURE = datetime(2099, 12, 31, 23, 0, tzinfo=timezone.utc)


class TestClosesAt:
    @pytest.fixture(autouse=True)
    def _setup(self, polls) -> None:
        self.poll = polls["p2"]

    def test_field(self):
        assert IPoll["close_date"].required is False
        assert self.poll.close_date is None

    def test_none(self):
        assert self.poll.closes_at() is None
        assert self.poll.expired is False

    def test_aware(self):
        self.poll.close_date = datetime(
            2026, 1, 1, 9, 0, tzinfo=timezone(timedelta(hours=-3))
        )
        assert self.poll.closes_at() == PAST

    def test_naive_is_utc(self):
        """A date stored without a timezone, as code may set it, is UTC."""
        self.poll.close_date = datetime(2026, 1, 1, 12, 0)
        assert self.poll.closes_at() == PAST
        assert self.poll.closes_at().tzinfo is timezone.utc

    def test_missing_attribute(self):
        """Polls saved before the field existed never expire."""
        self.poll.__dict__.pop("close_date", None)
        assert self.poll.expired is False

    @pytest.mark.parametrize(
        "close_date,expired",
        [
            (PAST, True),
            (FUTURE, False),
            (datetime(2026, 1, 1, 12, 0), True),
        ],
    )
    def test_expired(self, close_date, expired):
        self.poll.close_date = close_date
        assert self.poll.expired is expired

    def test_expired_at_the_closing_date(self, monkeypatch):
        """Voting ends at the closing date, not after it."""
        from collective.polls.content import poll as module

        class Now(datetime):
            @classmethod
            def now(cls, tz=None):
                return PAST

        monkeypatch.setattr(module, "datetime", Now)
        self.poll.close_date = PAST
        assert self.poll.expired is True
        self.poll.close_date = PAST + timedelta(seconds=1)
        assert self.poll.expired is False


class TestVoting:
    @pytest.fixture(autouse=True)
    def _setup(self, polls, http_request) -> None:
        self.poll = polls["p2"]
        self.request = http_request

    def test_before(self):
        self.poll.close_date = FUTURE
        assert self.poll.setVote(0, self.request) is True
        assert self.poll.total_votes == 1

    def test_after(self):
        self.poll.close_date = PAST
        with pytest.raises(PollClosed):
            self.poll.setVote(0, self.request)
        assert self.poll.total_votes == 0

    def test_after_having_voted(self):
        """A closed poll says so, rather than that the voter already voted."""
        self.poll.setVote(0, self.request)
        self.poll.close_date = PAST
        with pytest.raises(PollClosed):
            self.poll.setVote(1, self.request)
        assert self.poll.total_votes == 1

    def test_already_voted_unchanged(self):
        self.poll.setVote(0, self.request)
        with pytest.raises(AlreadyVoted):
            self.poll.setVote(1, self.request)
