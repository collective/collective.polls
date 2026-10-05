"""``IPollVotes``: what it stores, and that reading never writes."""

from . import VOTES_ANNO_KEY
from AccessControl import Unauthorized
from BTrees.IOBTree import IOBTree
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from BTrees.OOBTree import OOTreeSet
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import IPollVotes
from zope.annotation.interfaces import IAnnotations

import pytest
import transaction


def test_already_voted_is_unauthorized():
    """Code catching ``Unauthorized``, as 2.x callers do, still catches it."""
    assert issubclass(AlreadyVoted, Unauthorized)


class TestReadsNeverWrite:
    @pytest.fixture(autouse=True)
    def _setup(self, poll) -> None:
        self.poll = poll
        self.votes = IPollVotes(poll)
        transaction.savepoint()

    def test_no_storage_before_first_vote(self):
        assert IAnnotations(self.poll).get(VOTES_ANNO_KEY) is None

    def test_reads(self):
        assert self.votes.counts() == {0: 0, 1: 0, 2: 0}
        assert self.votes.orphans() == {}
        assert self.votes.total() == 0
        assert self.votes.voters() == []
        assert self.votes.has_voter("someone") is False
        assert self.poll.getResults() == []
        assert self.poll.total_votes == 0
        assert IAnnotations(self.poll).get(VOTES_ANNO_KEY) is None
        assert not self.poll._p_changed

    def test_clear_without_votes(self):
        self.votes.clear()
        assert IAnnotations(self.poll).get(VOTES_ANNO_KEY) is None
        assert not self.poll._p_changed


class TestRegister:
    @pytest.fixture(autouse=True)
    def _setup(self, poll) -> None:
        self.poll = poll
        self.votes = IPollVotes(poll)

    def test_register(self):
        self.votes.register(1, "member-a")
        self.votes.register(1, "Anonymous-xyz")
        self.votes.register(0, "member-b")
        assert self.votes.counts() == {0: 1, 1: 2, 2: 0}
        assert self.votes.total() == 3
        assert self.votes.voters() == ["Anonymous-xyz", "member-a", "member-b"]
        assert self.votes.has_voter("member-a") is True

    def test_counts_in_option_order(self):
        self.poll.options = list(reversed(self.poll.options))
        assert list(self.votes.counts()) == [2, 1, 0]

    def test_duplicate_voter(self):
        self.votes.register(1, "member-a")
        with pytest.raises(AlreadyVoted):
            self.votes.register(2, "member-a")
        assert self.votes.counts() == {0: 0, 1: 1, 2: 0}

    @pytest.mark.parametrize("option_id", [3, -1, "1", None])
    def test_unknown_option(self, option_id):
        with pytest.raises(ValueError):
            self.votes.register(option_id, "member-a")
        assert self.votes.voters() == []
        assert IAnnotations(self.poll).get(VOTES_ANNO_KEY) is None

    def test_stored_types(self):
        """Only BTrees types, so the data needs none of this package's code."""
        self.votes.register(1, "member-a")
        storage = IAnnotations(self.poll)[VOTES_ANNO_KEY]
        assert type(storage) is OOBTree
        assert type(storage["counts"]) is IOBTree
        assert type(storage["counts"][1]) is Length
        assert type(storage["voters"]) is OOTreeSet
        modules = {
            type(obj).__module__
            for obj in (
                storage,
                storage["counts"],
                storage["counts"][1],
                storage["voters"],
            )
        }
        assert all(name.startswith("BTrees.") for name in modules)


class TestOrphansAndClear:
    @pytest.fixture(autouse=True)
    def _setup(self, poll) -> None:
        self.poll = poll
        self.votes = IPollVotes(poll)
        self.votes.register(2, "member-a")
        self.votes.register(0, "member-b")

    def test_removed_option_becomes_orphan(self):
        self.poll.options = self.poll.options[:2]
        assert self.votes.counts() == {0: 1, 1: 0}
        assert self.votes.orphans() == {2: 1}
        assert self.votes.total() == 1
        assert self.poll.total_votes == 1

    def test_clear(self):
        self.votes.clear()
        assert self.votes.counts() == {0: 0, 1: 0, 2: 0}
        assert self.votes.voters() == []
        assert self.votes.total() == 0

    def test_clear_keeps_orphans(self):
        """As 2.x did on reject: only the current options are reset."""
        self.poll.options = self.poll.options[:2]
        self.votes.clear()
        assert self.votes.orphans() == {2: 1}
        assert self.votes.counts() == {0: 0, 1: 0}

    def test_merge(self):
        """Bulk counts add to stored ones, for current and gone options."""
        self.votes.merge({2: 3, 9: 1}, ["member-a", "member-c"])
        assert self.votes.counts() == {0: 1, 1: 0, 2: 4}
        assert self.votes.orphans() == {9: 1}
        assert self.votes.voters() == ["member-a", "member-b", "member-c"]

    def test_vote_again_after_clear(self):
        self.votes.clear()
        self.votes.register(1, "member-a")
        assert self.votes.counts() == {0: 0, 1: 1, 2: 0}
