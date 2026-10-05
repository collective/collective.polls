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
from plone.dexterity.content import Container
from plone.schema import JSONField
from plone.supermodel import model
from plone.supermodel.directives import fieldset
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


class TooManyChoices(Invalid):
    """A poll lets voters pick more options than it has."""


class IPoll(model.Schema):
    """A Poll in a Plone site."""

    fieldset(
        "voting",
        label=_("Voting"),
        fields=[
            "allow_anonymous",
            "max_choices",
            "legend",
            "options",
            "shuffle_options",
        ],
    )
    fieldset(
        "results",
        label=_("Results"),
        fields=["show_results", "results_graph"],
    )

    allow_anonymous = schema.Bool(
        title=_("Allow anonymous"),
        description=_(
            "Allow not logged in users to vote. "
            "The parent folder of this poll should be published before opening "
            "the poll for this field to take effect"
        ),
        default=True,
    )

    max_choices = schema.Int(
        title=_("Number of options a voter can pick"),
        description=_(
            "1 makes a single choice poll. More than 1 lets voters pick up to "
            "that many options."
        ),
        default=1,
        min=1,
        required=True,
    )

    legend = schema.TextLine(
        title=_("Legend"),
        description=_(
            "Shown above the options. Leave empty for "
            '"Select one option" or "Select up to N options".'
        ),
        required=False,
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

    shuffle_options = schema.Bool(
        title=_("Shuffle options"),
        description=_(
            "Show the options in a random order to each voter, so their "
            "position does not favor any of them."
        ),
        default=False,
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

    @invariant
    def validate_max_choices(data: Any) -> None:
        """Keep the number of options a voter can pick within the options.

        :param data: The object or form data being validated.
        :raises TooManyChoices: When it exceeds the number of options.
        """
        max_choices = getattr(data, "max_choices", None) or 1
        if max_choices > len(data.options or []):
            raise TooManyChoices(
                _("Voters cannot pick more options than the poll has.")
            )


@implementer(IPoll)
class Poll(Container):
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

    @property
    def multiple_choice(self) -> bool:
        """Whether a voter can pick more than one option."""
        return (self.max_choices or 1) > 1

    def getResults(self) -> list[tuple[str, int, float]]:
        """Return the results so far.

        :returns: ``(description, votes, fraction)`` per option, in option
            order; an empty list while nobody voted. The fraction is of
            :attr:`total_votes`, so in a multiple choice poll it is the share
            of voters who picked the option.
        """
        counts = IPollVotes(self).counts()
        total = self.total_votes
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
        """Number of votes so far: one per voter, whatever they picked.

        A single choice poll counts the votes for its current options; a
        multiple choice poll counts its voters, since one voter adds a vote
        to several options.
        """
        votes = IPollVotes(self)
        return votes.voter_count() if self.multiple_choice else votes.total()

    def _chosen(self, option: Any) -> list[int] | None:
        """Read the options a vote picks.

        :param option: One option id, or a list of them.
        :returns: The ids, in the order given; ``None`` unless they are 1 to
            ``max_choices`` distinct ids of this poll's options.
        """
        chosen = option if isinstance(option, list | tuple) else [option]
        valid = {o["option_id"] for o in self.getOptions()}
        if not chosen or len(chosen) > (self.max_choices or 1):
            return None
        for option_id in chosen:
            if isinstance(option_id, bool) or option_id not in valid:
                return None
        if len(set(chosen)) != len(chosen):
            return None
        return list(chosen)

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

        :param option: Id of the option voted for, or a list of 1 to
            ``max_choices`` distinct ids.
        :param request: Request carrying, and receiving, the anonymous cookie.
        :returns: ``True`` when the vote was counted; ``False`` for anything
            that is not such an id or list of ids.
        :raises Unauthorized: Without the vote permission.
        :raises AlreadyVoted: When the caller already voted, or is anonymous
            and there is no request to tell by.
        """
        getUtility(IPolls, name="collective.polls").allowed_to_vote(self, request)
        chosen = self._chosen(option)
        if chosen is None:
            return False
        voter_id = api.user.get_current().getId() or self._anonymous_voter(request)
        IPollVotes(self).register(chosen, voter_id)
        notify(ObjectModifiedEvent(self))
        return True
