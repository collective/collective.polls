"""Module where all interfaces, events and exceptions live."""

from AccessControl import Unauthorized
from typing import TypedDict
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class AlreadyVoted(Unauthorized):
    """The caller already voted in this poll.

    A subclass of ``Unauthorized``, so code written for the 2.x API, which
    raised ``Unauthorized`` for this case too, keeps working.
    """


class _PollOptionBase(TypedDict):
    description: str


class PollOptionDict(_PollOptionBase, total=False):
    """One option of a poll.

    ``option_id`` is missing only on an option that was never saved.
    """

    option_id: int


class IPollVotes(Interface):
    """The votes of one poll.

    Adapt a poll to this interface to read or record votes. Reading never
    writes to the database: storage is created on the first vote.
    """

    def counts() -> dict[int, int]:
        """Votes per option id, for every current option, zero included."""

    def orphans() -> dict[int, int]:
        """Votes recorded for option ids the poll no longer has."""

    def total() -> int:
        """Number of votes for the current options."""

    def voters() -> list[str]:
        """Ids of everyone who voted, sorted."""

    def has_voter(voter_id: str) -> bool:
        """Check whether a voter id already voted."""

    def register(option_id: int, voter_id: str) -> None:
        """Record one vote for an option.

        Raises ``ValueError`` for an option id the poll does not have, and
        ``AlreadyVoted`` for a voter id that already voted.
        """

    def clear() -> None:
        """Remove the votes of the current options, and every voter."""
