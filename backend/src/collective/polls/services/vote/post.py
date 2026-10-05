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

    def _option_id(self) -> int | None:
        """Read the option id from the request body.

        :returns: The option id, or ``None`` when the body is not a JSON
            object with an integer ``option_id``.
        """
        try:
            data = json.loads(self.request.get("BODY") or "")
        except ValueError:
            return None
        option_id = data.get("option_id") if isinstance(data, dict) else None
        if isinstance(option_id, bool) or not isinstance(option_id, int):
            return None
        return option_id

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
        option_id = self._option_id()
        if option_id is None:
            return self._error(
                400,
                "BadRequest",
                _("The request body must be a JSON object with an integer option_id."),
            )
        try:
            voted = self.context.setVote(option_id, self.request)
        except AlreadyVoted:
            return self._error(
                403, "AlreadyVoted", _("You already voted in this poll.")
            )
        if not voted:
            return self._error(400, "BadRequest", _("This poll has no such option."))
        return self.poll_state(has_voted=True)
