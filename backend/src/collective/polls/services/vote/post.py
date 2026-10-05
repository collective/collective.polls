"""``POST @vote``."""

from collective.polls import _
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import PollStateDict
from collective.polls.services import PollService
from collective.polls.services import PRIVATE_CACHE_CONTROL
from plone.protect.interfaces import IDisableCSRFProtection
from typing import Any
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import alsoProvides

import json


class VotePost(PollService):
    """Record the current user's vote in a poll."""

    def _error(self, status: int, kind: str, message: Message) -> dict[str, Any]:
        """Set a response status and render an error body.

        :param status: HTTP status to answer with.
        :param kind: Short error type.
        :param message: Message to translate for the caller.
        :returns: The error body.
        """
        self.request.response.setStatus(status)
        return {
            "error": {"type": kind, "message": translate(message, context=self.request)}
        }

    def _option_ids(self) -> list[int] | None:
        """Read the chosen option ids from the request body.

        The body holds either ``option_id``, one integer, or ``option_ids``,
        a non-empty list of integers, as a multiple choice poll needs.

        :returns: The option ids, or ``None`` when the body is not a JSON
            object with exactly one of those keys, well formed.
        """
        try:
            data = json.loads(self.request.get("BODY") or "")
        except ValueError:
            return None
        if not isinstance(data, dict) or ("option_id" in data) == (
            "option_ids" in data
        ):
            return None
        chosen = data["option_ids"] if "option_ids" in data else [data["option_id"]]
        if not isinstance(chosen, list) or not chosen:
            return None
        for option_id in chosen:
            if isinstance(option_id, bool) or not isinstance(option_id, int):
                return None
        return chosen

    def reply(self) -> PollStateDict | dict[str, Any]:
        """Record a vote and answer the new state of the poll.

        The answer says ``has_voted: true`` for anonymous callers too: this
        one response is the moment the server knows. Nothing is written
        unless the vote is recorded.

        :returns: The ``@poll`` payload, or an error body.
        """
        # plone.protect refuses writes by members that carry no CSRF token,
        # and a REST client has none to send. Anonymous writes are not
        # checked at all.
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.response.setHeader("Cache-Control", PRIVATE_CACHE_CONTROL)
        option_ids = self._option_ids()
        if option_ids is None:
            return self._error(
                400,
                "BadRequest",
                _(
                    "The request body must be a JSON object with an integer "
                    "option_id or a list of integers option_ids."
                ),
            )
        try:
            voted = self.context.setVote(option_ids, self.request)
        except AlreadyVoted:
            return self._error(
                403, "AlreadyVoted", _("You already voted in this poll.")
            )
        if not voted:
            if not self.context.multiple_choice:
                return self._error(
                    400, "BadRequest", _("This poll has no such option.")
                )
            return self._error(
                400,
                "BadRequest",
                _(
                    "Pick from 1 to ${count} of this poll's options, each once.",
                    mapping={"count": self.context.max_choices},
                ),
            )
        return self.poll_state(has_voted=True)
