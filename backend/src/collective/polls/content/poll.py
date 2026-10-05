"""The Poll content type."""

from __future__ import annotations

from collective.polls import _
from collective.polls.config import ANONYMOUS_PREFIX
from collective.polls.config import COOKIE_KEY
from collective.polls.config import COOKIE_MAX_AGE
from collective.polls.config import PERMISSION_VOTE
from collective.polls.interfaces import IPollVotes
from collective.polls.interfaces import PollOptionDict
from collective.polls.options import DuplicateOptionId
from collective.polls.options import normalize_options
from collective.polls.options import OPTIONS_SCHEMA
from collective.polls.utility import IPolls
from plone import api
from plone.dexterity.content import Item
from plone.schema import JSONField
from plone.supermodel import model
from typing import Any
from typing import TYPE_CHECKING
from zope import schema
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.lifecycleevent import ObjectModifiedEvent


if TYPE_CHECKING:
    from ZPublisher.HTTPRequest import HTTPRequest


class InsufficientOptions(Invalid):
    """A poll needs at least two options."""

    __doc__ = _("Not enough options provided")


#: Misspelled name kept for code that imports it.
InsuficientOptions = InsufficientOptions


class DuplicateOptions(Invalid):
    """Two options of a poll share an id."""


class IPoll(model.Schema):
    """A Poll in a Plone site."""

    allow_anonymous = schema.Bool(
        title=_("Allow anonymous"),
        description=_(
            "Allow not logged in users to vote. "
            "The parent folder of this poll should be published before opening "
            "the poll for this field to take effect"
        ),
        default=True,
    )

    show_results = schema.Bool(
        title=_("Show partial results"),
        description=_("Show partial results after a voter has already voted."),
        default=True,
    )

    results_graph = schema.Choice(
        title=_("Graph"),
        description=_("Format to show the results."),
        default="bar",
        required=True,
        vocabulary="collective.polls.ResultsGraph",
    )

    options = JSONField(
        title=_("Available options"),
        schema=OPTIONS_SCHEMA,
        widget="poll_options",
        defaultFactory=list,
        required=True,
    )

    @invariant
    def validate_options(data: Any) -> None:
        """Require at least two options, with distinct ids.

        :param data: The object or form data being validated.
        :raises InsufficientOptions: With fewer than two options.
        :raises DuplicateOptions: When two options share an id.
        """
        if len(data.options or []) < 2:
            raise InsufficientOptions(
                _("You need to provide at least two options for a poll.")
            )
        try:
            normalize_options(data.options)
        except DuplicateOptionId:
            raise DuplicateOptions(_("Two options cannot share an id.")) from None


# IPoll extends plone.supermodel's model.Schema; mypy-zope does not recognize
# the class plone-stubs declares for it as an interface.
@implementer(IPoll)  # type: ignore[misc]
class Poll(Item):
    """A Poll in a Plone site."""

    # Declaring the vote permission on the class is what makes it a valid
    # permission on a poll: without it, ``manage_permission`` and
    # ``rolesOfPermission`` reject it, and the workflow cannot map it.
    __ac_permissions__ = ((PERMISSION_VOTE, ("setVote",)),)

    def getOptions(self) -> list[PollOptionDict]:
        """Return the options of this poll.

        :returns: One ``{"option_id": int, "description": str}`` per option.
        """
        return self.options or []

    def getResults(self) -> list[tuple[str, int, float]]:
        """Return the results so far.

        :returns: ``(description, votes, fraction)`` per option, in option
            order; an empty list while nobody voted.
        """
        counts = IPollVotes(self).counts()
        total = sum(counts.values())
        if total == 0:
            return []
        return [
            (
                option["description"],
                counts[option["option_id"]],
                counts[option["option_id"]] / total,
            )
            for option in self.getOptions()
        ]

    def voters(self) -> list[str]:
        """Return the ids of everyone who voted.

        :returns: Member ids, and ``Anonymous-<id>`` for anonymous voters,
            sorted.
        """
        return IPollVotes(self).voters()

    @property
    def total_votes(self) -> int:
        """Number of votes so far."""
        return IPollVotes(self).total()

    def _anonymous_voter(self, request: Any) -> str:
        """Give an anonymous voter a random id, sent back in a cookie.

        The cookie is how the voter is recognized next time. It is readable
        by scripts on purpose: the browser checks it to know whether the
        visitor voted, which keeps the poll's own responses cacheable.

        :param request: Request whose response carries the cookie. Never
            ``None`` here: ``allowed_to_vote`` refuses an anonymous voter
            without a request, since it cannot tell whether they voted.
        :returns: The voter id to record.
        """
        utility = getUtility(IPolls, name="collective.polls")
        vote_id = utility.anonymous_vote_id()
        request.response.setCookie(
            COOKIE_KEY + api.content.get_uuid(self),
            vote_id,
            path="/",
            max_age=COOKIE_MAX_AGE,
            same_site="Lax",
            secure=request.get("SERVER_URL", "").startswith("https://"),
        )
        return f"{ANONYMOUS_PREFIX}{vote_id}"

    def setVote(self, option: Any = None, request: HTTPRequest | None = None) -> bool:
        """Vote in this poll as the current user.

        :param option: Id of the option voted for.
        :param request: Request carrying, and receiving, the anonymous cookie.
        :returns: ``True`` when the vote was counted; ``False`` for anything
            that is not the id of one of the options.
        :raises Unauthorized: Without the vote permission.
        :raises AlreadyVoted: When the caller already voted, or is anonymous
            and there is no request to tell by.
        """
        getUtility(IPolls, name="collective.polls").allowed_to_vote(self, request)
        option_ids = [o["option_id"] for o in self.getOptions()]
        if isinstance(option, bool) or option not in option_ids:
            return False
        voter_id = api.user.get_current().getId() or self._anonymous_voter(request)
        IPollVotes(self).register(option, voter_id)
        notify(ObjectModifiedEvent(self))
        return True
