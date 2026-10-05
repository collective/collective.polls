"""The state of a poll, as both REST services report it."""

from collective.polls.config import PERMISSION_VOTE
from collective.polls.content.poll import IPoll
from collective.polls.content.poll import Poll
from collective.polls.interfaces import IPollVotes
from collective.polls.interfaces import ISerializePollState
from collective.polls.interfaces import PollResultDict
from collective.polls.interfaces import PollStateDict
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from ZPublisher.HTTPRequest import HTTPRequest


def results_visible(poll: Poll, has_voted: bool | None) -> bool:
    """Decide whether the current user gets the results of a poll.

    Closed polls show their results to everyone, and reviewers always see
    them. While a poll is open, ``show_results`` lets people who voted see
    them. Anonymous callers (``has_voted`` is ``None``) get them on the same
    terms as voters: their answer must not depend on who asks, so it can be
    cached, and the browser hides the numbers until the visitor's cookie
    says they voted.

    :param poll: The poll.
    :param has_voted: Whether the caller voted; ``None`` for anonymous.
    :returns: ``True`` when the results are part of the answer.
    """
    state = api.content.get_state(poll)
    if state == "closed":
        return True
    if api.user.has_permission("Review portal content", obj=poll):
        return True
    return state == "open" and poll.show_results and has_voted is not False


def anonymous_blocked(poll: Poll, state: str) -> bool:
    """Tell whether anonymous visitors cannot vote in a poll meant for them.

    That happens when the poll was opened while its parent folder was not
    published: the workflow subscriber only grants the vote to anonymous
    visitors who can see the poll.

    :param poll: The poll.
    :param state: The poll's workflow state.
    :returns: ``True`` for an open poll allowing anonymous votes that
        Anonymous cannot vote in.
    """
    if state != "open" or not poll.allow_anonymous:
        return False
    roles = [
        r["name"] for r in poll.rolesOfPermission(PERMISSION_VOTE) if r["selected"]
    ]
    return "Anonymous" not in roles


def build_results(poll: Poll) -> list[PollResultDict]:
    """Return the votes for each option, in option order.

    :param poll: The poll.
    :returns: One entry per option, with a fraction of ``0.0`` for every
        option while nobody voted. The fraction is of the poll's
        ``total_votes``: in a multiple choice poll, the share of voters.
    """
    counts = IPollVotes(poll).counts()
    total = poll.total_votes
    return [
        {
            "option_id": option["option_id"],
            "description": option["description"],
            "votes": counts[option["option_id"]],
            "percentage": counts[option["option_id"]] / total if total else 0.0,
        }
        for option in poll.getOptions()
    ]


@implementer(ISerializePollState)
@adapter(IPoll, Interface)
class PollStateSerializer:
    """Build the ``@poll`` payload for a poll and a request."""

    def __init__(self, context: Poll, request: HTTPRequest) -> None:
        """Bind the serializer to a poll and a request.

        :param context: The poll.
        :param request: The current request.
        """
        self.context = context
        self.request = request

    def _has_voted(self) -> bool | None:
        """Tell whether the current member voted.

        :returns: ``None`` for anonymous callers: only the browser knows,
            from the cookie, and the answer has to be the same for every
            anonymous visitor.
        """
        member_id = api.user.get_current().getId()
        if not member_id:
            return None
        return IPollVotes(self.context).has_voter(member_id)

    def __call__(self, has_voted: bool | None = None) -> PollStateDict:
        """Return the state of the poll, as seen by the current user.

        :param has_voted: Override for ``has_voted``; the vote service passes
            ``True`` right after recording a vote.
        :returns: The ``@poll`` payload.
        """
        poll = self.context
        state = api.content.get_state(poll)
        if has_voted is None:
            has_voted = self._has_voted()
        visible = results_visible(poll, has_voted)
        return {
            "@id": f"{poll.absolute_url()}/@poll",
            "uid": api.content.get_uuid(poll),
            "state": state,
            "allow_anonymous": bool(poll.allow_anonymous),
            "anonymous_blocked": anonymous_blocked(poll, state),
            "show_results": bool(poll.show_results),
            "results_graph": poll.results_graph,
            "options": poll.getOptions(),
            "max_choices": poll.max_choices or 1,
            "legend": poll.legend or None,
            "shuffle_options": bool(poll.shuffle_options),
            "can_vote": bool(api.user.has_permission(PERMISSION_VOTE, obj=poll)),
            "has_voted": has_voted,
            "total_votes": poll.total_votes if visible else None,
            "results": build_results(poll) if visible else None,
        }
