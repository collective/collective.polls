"""Module where all interfaces, events and exceptions live."""

from AccessControl import Unauthorized
from collections.abc import Iterable
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


class PollResultDict(TypedDict):
    """Votes for one option, as the ``@poll`` service reports them."""

    option_id: int
    description: str
    votes: int
    #: Share of the votes, a fraction in ``[0, 1]``; ``0.0`` with no votes.
    percentage: float


# A functional TypedDict, since ``@id`` is not a Python identifier.
PollStateDict = TypedDict(
    "PollStateDict",
    {
        "@id": str,
        "uid": str,
        "state": str,
        "allow_anonymous": bool,
        "anonymous_blocked": bool,
        "show_results": bool,
        "results_graph": str,
        "options": list[PollOptionDict],
        "can_vote": bool,
        "has_voted": bool | None,
        "total_votes": int | None,
        "results": list[PollResultDict] | None,
    },
)
PollStateDict.__doc__ = """The state of a poll, as the ``@poll`` service reports it."""


class ISerializePollState(Interface):
    """Build the ``@poll`` payload for a poll and a request.

    Registered as a multi-adapter of the poll and the request, so both
    services answer with exactly the same shape.
    """

    def __call__(has_voted: bool | None = None) -> PollStateDict:
        """Return the state of the poll, as seen by the current user.

        :param has_voted: Override for ``has_voted``; the vote service passes
            ``True`` right after recording a vote.
        """


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

    def merge(counts: dict[int, int], voters: Iterable[str]) -> None:
        """Add votes in bulk, as a migration or an import does.

        Counts are added to what is stored, for any option id, current or
        not, and voters join the stored ones. Nothing is validated: the
        votes were valid where they came from.
        """
