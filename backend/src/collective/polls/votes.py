"""Vote storage for polls.

Votes live in one annotation on the poll, holding BTrees types only:

* ``counts``: an ``IOBTree`` mapping an option id to a ``BTrees.Length``;
* ``voters``: an ``OOTreeSet`` of voter ids.

There is no persistent class of this package's own in the stored data, so
the votes stay readable whether or not the add-on code is importable.

Version 2.x kept the voters in a plain list that was written whole on every
vote; a tree set writes only the bucket that changed.
"""

from BTrees.IOBTree import IOBTree
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from BTrees.OOBTree import OOTreeSet
from collections.abc import Iterable
from collective.polls.config import VOTES_ANNO_KEY
from collective.polls.content.poll import IPoll
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import IPollVotes
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer


@implementer(IPollVotes)
@adapter(IPoll)
class PollVotes:
    """The votes of one poll, kept in its annotations."""

    def __init__(self, context: IPoll) -> None:
        self.context = context

    def _storage(self) -> OOBTree | None:
        """Return the stored votes, or ``None`` before the first vote."""
        return IAnnotations(self.context).get(VOTES_ANNO_KEY)

    def _create_storage(self) -> OOBTree:
        """Return the stored votes, creating the storage when missing."""
        storage = self._storage()
        if storage is None:
            storage = OOBTree()
            storage["counts"] = IOBTree()
            storage["voters"] = OOTreeSet()
            IAnnotations(self.context)[VOTES_ANNO_KEY] = storage
        return storage

    def _option_ids(self) -> list[int]:
        """Ids of the poll's current options, in option order."""
        return [option["option_id"] for option in self.context.getOptions()]

    def _stored_counts(self) -> dict[int, int]:
        """Every stored count, whether or not its option still exists."""
        storage = self._storage()
        if storage is None:
            return {}
        return {option_id: length() for option_id, length in storage["counts"].items()}

    def counts(self) -> dict[int, int]:
        """Votes per option id, for every current option, zero included.

        :returns: Option id to number of votes, in option order.
        """
        stored = self._stored_counts()
        return {option_id: stored.get(option_id, 0) for option_id in self._option_ids()}

    def orphans(self) -> dict[int, int]:
        """Votes recorded for option ids the poll no longer has.

        :returns: Option id to number of votes.
        """
        current = set(self._option_ids())
        return {
            option_id: votes
            for option_id, votes in self._stored_counts().items()
            if option_id not in current
        }

    def total(self) -> int:
        """Number of votes for the current options.

        :returns: The sum of :meth:`counts`.
        """
        return sum(self.counts().values())

    def voters(self) -> list[str]:
        """Ids of everyone who voted.

        :returns: Member ids and ``Anonymous-<id>`` strings, sorted.
        """
        storage = self._storage()
        return sorted(storage["voters"]) if storage is not None else []

    def has_voter(self, voter_id: str) -> bool:
        """Check whether a voter id already voted.

        :param voter_id: A member id, or ``Anonymous-<id>``.
        :returns: ``True`` when the id is among the voters.
        """
        storage = self._storage()
        return storage is not None and voter_id in storage["voters"]

    def register(self, option_id: int, voter_id: str) -> None:
        """Record one vote for an option.

        :param option_id: Id of one of the poll's options.
        :param voter_id: A member id, or ``Anonymous-<id>``.
        :raises ValueError: For an option id the poll does not have.
        :raises AlreadyVoted: When the voter already voted.
        """
        if option_id not in self._option_ids():
            raise ValueError(f"Unknown option id: {option_id!r}")
        if self.has_voter(voter_id):
            raise AlreadyVoted(voter_id)
        storage = self._create_storage()
        storage["voters"].add(voter_id)
        counts = storage["counts"]
        if option_id not in counts:
            counts[option_id] = Length()
        counts[option_id].change(1)

    def clear(self) -> None:
        """Remove every voter and the votes of the current options.

        Votes kept for option ids the poll no longer has are left alone, as
        2.x did when a poll was rejected.
        """
        storage = self._storage()
        if storage is None:
            return
        storage["voters"].clear()
        counts = storage["counts"]
        for option_id in self._option_ids():
            if option_id in counts:
                del counts[option_id]

    def merge(self, counts: dict[int, int], voters: Iterable[str]) -> None:
        """Add votes in bulk, as a migration or an import does.

        :param counts: Option id to number of votes to add; ids need not be
            current options, so nothing recorded is dropped.
        :param voters: Voter ids to add to the stored ones.
        """
        storage = self._create_storage()
        storage["voters"].update(voters)
        stored = storage["counts"]
        for option_id, votes in counts.items():
            if option_id not in stored:
                stored[option_id] = Length()
            stored[option_id].change(votes)
