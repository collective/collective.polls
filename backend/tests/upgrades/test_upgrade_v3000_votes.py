"""Upgrade to 3000: votes move from the 2.x annotations to the 3.0 storage."""

from . import oracle
from .legacy import make_legacy_poll
from .legacy import random_legacy_votes
from collective.polls.config import VOTES_ANNO_KEY
from collective.polls.interfaces import IPollVotes
from collective.polls.upgrades.v3000 import votes as step
from collective.polls.votes import PollVotes
from zope.annotation.interfaces import IAnnotations

import logging
import pytest


SEEDS = range(12)

OPTIONS = [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"},
]

MERGE = PollVotes.merge


def legacy_keys(poll) -> list[str]:
    return [
        key
        for key in IAnnotations(poll)
        if key == "voters_members_id" or key.startswith("option.")
    ]


class TestOracle:
    """For random 2.x polls, 3.0 reports what 2.x reported."""

    @pytest.fixture(autouse=True)
    def _setup(self, folder, run_step) -> None:
        self.folder = folder
        self.run_step = run_step

    @pytest.mark.parametrize("seed", SEEDS)
    def test_results(self, seed):
        options, voters, counts = random_legacy_votes(seed)
        poll = make_legacy_poll(self.folder, "poll", options, voters, counts)
        expected = oracle.get_results(options, dict(IAnnotations(poll)))
        total = oracle.total_votes(options, dict(IAnnotations(poll)))
        self.run_step(step.migrate_votes)
        assert poll.getResults() == expected
        assert poll.total_votes == total
        assert set(poll.voters()) == set(voters)
        assert len(poll.voters()) == len(set(voters))
        assert legacy_keys(poll) == []

    @pytest.mark.parametrize("seed", SEEDS)
    def test_second_run_changes_nothing(self, seed):
        options, voters, counts = random_legacy_votes(seed)
        poll = make_legacy_poll(self.folder, "poll", options, voters, counts)
        self.run_step(step.migrate_votes)
        before = (IPollVotes(poll).counts(), IPollVotes(poll).voters())
        assert step.migrate_poll(poll) is False
        assert (IPollVotes(poll).counts(), IPollVotes(poll).voters()) == before

    def test_many_polls(self, monkeypatch):
        """Savepoints between batches do not lose anything."""
        monkeypatch.setattr(step, "BATCH_SIZE", 2)
        polls = []
        for seed in range(5):
            options, voters, counts = random_legacy_votes(seed)
            poll = make_legacy_poll(
                self.folder, f"poll-{seed}", options, voters, counts
            )
            expected = oracle.get_results(options, dict(IAnnotations(poll)))
            polls.append((poll, expected))
        self.run_step(step.migrate_votes)
        for poll, expected in polls:
            assert poll.getResults() == expected


class TestEdgeCases:
    @pytest.fixture(autouse=True)
    def _setup(self, folder, run_step) -> None:
        self.folder = folder
        self.run_step = run_step

    def make(self, options=OPTIONS, voters=(), counts=None):
        return make_legacy_poll(
            self.folder, "poll", options, list(voters), counts or {}
        )

    def test_poll_without_votes_skipped(self):
        poll = make_legacy_poll(self.folder, "poll", OPTIONS, [], {})
        del IAnnotations(poll)["voters_members_id"]
        assert step.migrate_poll(poll) is False
        assert IAnnotations(poll).get(VOTES_ANNO_KEY) is None

    def test_voters_only(self):
        """2.x wrote the voter list on every vote; counts may be missing."""
        poll = self.make(voters=["a", "b"])
        expected = oracle.get_results(OPTIONS, dict(IAnnotations(poll)))
        assert step.migrate_poll(poll) is True
        assert poll.voters() == ["a", "b"]
        assert poll.total_votes == 0
        assert poll.getResults() == expected == []

    def test_counts_only(self):
        poll = self.make(counts={1: 4})
        del IAnnotations(poll)["voters_members_id"]
        assert step.migrate_poll(poll) is True
        assert IPollVotes(poll).counts() == {0: 0, 1: 4}

    def test_unpadded_key(self):
        """``option.1`` and ``option.01`` both count for option 1."""
        poll = self.make(counts={1: 4})
        IAnnotations(poll)["option.1"] = 2
        step.migrate_poll(poll)
        assert IPollVotes(poll).counts() == {0: 0, 1: 6}
        assert legacy_keys(poll) == []

    @pytest.mark.parametrize(
        "options",
        [
            ["Yes", "No"],
            [{"description": "Yes"}, {"description": "No"}],
            ["Yes", {"description": "No"}],
        ],
        ids=["strings", "no-ids", "mixed"],
    )
    def test_options_without_ids(self, options):
        """They get their position as id, which is what 2.x counted by."""
        poll = self.make(options=options, voters=["a", "b", "c"], counts={0: 1, 1: 2})
        step.migrate_poll(poll)
        assert poll.options == OPTIONS
        assert poll.getResults() == [("Yes", 1, 1 / 3), ("No", 2, 2 / 3)]

    def test_options_already_with_ids_untouched(self):
        poll = self.make(counts={0: 1})
        options = poll.options
        step.migrate_poll(poll)
        assert poll.options is options

    def test_orphans_kept(self, caplog):
        """Counts for options the poll no longer has are kept, and logged."""
        poll = self.make(voters=["a", "b", "c"], counts={0: 1, 7: 2})
        with caplog.at_level(logging.WARNING):
            step.migrate_poll(poll)
        assert IPollVotes(poll).counts() == {0: 1, 1: 0}
        assert IPollVotes(poll).orphans() == {7: 2}
        assert "{7: 2}" in caplog.text

    def test_votes_cast_before_the_upgrade_kept(self):
        """Votes cast on 3.0 code before the step ran are added to."""
        poll = self.make(voters=["a"], counts={0: 1})
        IPollVotes(poll).register(1, "b")
        step.migrate_poll(poll)
        assert IPollVotes(poll).counts() == {0: 1, 1: 1}
        assert poll.voters() == ["a", "b"]

    @pytest.mark.parametrize(
        "broken_merge",
        [
            lambda self, counts, voters: MERGE(
                self, {k: v - 1 for k, v in counts.items()}, voters
            ),
            lambda self, counts, voters: MERGE(self, counts, list(voters)[1:]),
        ],
        ids=["counts", "voters"],
    )
    def test_check_fires(self, monkeypatch, broken_merge):
        """A migration that loses votes stops, and keeps the 2.x data."""
        monkeypatch.setattr(PollVotes, "merge", broken_merge)
        poll = self.make(voters=["a", "b"], counts={0: 1, 1: 1})
        with pytest.raises(step.MigrationError):
            step.migrate_poll(poll)
        assert sorted(legacy_keys(poll)) == [
            "option.00",
            "option.01",
            "voters_members_id",
        ]
