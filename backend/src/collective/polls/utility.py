"""The ``IPolls`` utility: the package's public Python API for polls.

Registered as a named utility, ``collective.polls``, so code outside this
package can find polls and ask permission questions about them without
importing the content class.
"""

from __future__ import annotations

from AccessControl import Unauthorized
from collective.polls.config import ANONYMOUS_PREFIX
from collective.polls.config import COOKIE_KEY
from collective.polls.config import PERMISSION_VOTE
from collective.polls.config import PORTAL_TYPE
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import IPollVotes
from plone import api
from typing import Any
from typing import TYPE_CHECKING
from zope.interface import implementer
from zope.interface import Interface

import secrets


if TYPE_CHECKING:
    from collective.polls.content.poll import Poll
    from ZPublisher.HTTPRequest import HTTPRequest


class IPolls(Interface):
    """Utility methods for dealing with polls."""

    def recent_polls(
        context: Any = None, show_all: bool = False, limit: int = 5, **kw: Any
    ) -> list:
        """Return catalog brains of the most recently created polls."""

    def poll_by_uid(uid: str, context: Any = None) -> Poll | None:
        """Return the poll with the given UID, or the latest open one."""

    def voted_in_a_poll(poll: Poll, request: HTTPRequest | None = None) -> bool:
        """Check whether the current user already voted in a poll."""

    def allowed_to_edit(poll: Poll) -> bool:
        """Check whether the current user may edit a poll."""

    def allowed_to_view(poll: Poll) -> bool:
        """Check whether the current user may view a poll."""

    def allowed_to_vote(poll: Poll, request: HTTPRequest | None = None) -> bool:
        """Return ``True`` when the current user may vote, else raise."""

    def anonymous_vote_id() -> str:
        """Return a new identifier for an anonymous vote."""


@implementer(IPolls)
class Polls:
    """Utility methods for dealing with polls."""

    def recent_polls(
        self,
        context: Any = None,
        show_all: bool = False,
        limit: int = 5,
        **kw: Any,
    ) -> list:
        """Return catalog brains of the most recently created polls.

        :param context: Restrict the search to this container, when given.
        :param show_all: Include polls in every state, not only open ones.
        :param limit: Maximum number of brains to return.
        :param kw: Extra catalog query arguments.
        :returns: Brains, newest first.
        """
        if context is not None:
            kw["path"] = "/".join(context.getPhysicalPath())
        kw["portal_type"] = PORTAL_TYPE
        kw["sort_on"] = "created"
        kw["sort_order"] = "reverse"
        kw["sort_limit"] = limit
        if not show_all:
            kw["review_state"] = "open"
        results = api.content.find(**kw)
        return list(results)[:limit]

    def poll_by_uid(self, uid: str, context: Any = None) -> Poll | None:
        """Return the poll with the given UID.

        :param uid: UID of a poll, or ``latest`` for the newest open poll.
        :param context: Container to search in when ``uid`` is ``latest``.
        :returns: The poll, or ``None`` when there is none.
        """
        if uid == "latest":
            results = self.recent_polls(context=context, show_all=False, limit=1)
        else:
            results = list(api.content.find(UID=uid))
        return results[0].getObject() if results else None

    def voted_in_a_poll(self, poll: Poll, request: HTTPRequest | None = None) -> bool:
        """Check whether the current user already voted in a poll.

        Members are looked up by id. Anonymous visitors are recognized by the
        cookie set when they voted. When there is no way to tell -- an
        anonymous visitor on a poll closed to anonymous votes, or no request
        to read the cookie from -- the answer is ``True``, so nobody gets to
        vote twice by being unrecognizable.

        :param poll: The poll.
        :param request: Request carrying the anonymous voting cookie.
        :returns: ``True`` when the user voted, or when it cannot be told.
        """
        votes = IPollVotes(poll)
        member_id = api.user.get_current().getId()
        if member_id:
            return votes.has_voter(member_id)
        if poll.allow_anonymous and request is not None:
            value = request.cookies.get(COOKIE_KEY + api.content.get_uuid(poll), "")
            return bool(value) and votes.has_voter(f"{ANONYMOUS_PREFIX}{value}")
        return True

    def allowed_to_edit(self, poll: Poll) -> bool:
        """Check whether the current user may edit a poll.

        :param poll: The poll.
        :returns: ``True`` with ``Modify portal content`` on the poll.
        """
        return api.user.has_permission("Modify portal content", obj=poll)

    def allowed_to_view(self, poll: Poll) -> bool:
        """Check whether the current user may view a poll.

        :param poll: The poll.
        :returns: ``True`` with ``View`` on the poll.
        """
        return api.user.has_permission("View", obj=poll)

    def allowed_to_vote(self, poll: Poll, request: HTTPRequest | None = None) -> bool:
        """Check whether the current user may vote in a poll now.

        :param poll: The poll.
        :param request: Request carrying the anonymous voting cookie.
        :returns: ``True``; every other case raises.
        :raises Unauthorized: Without the vote permission.
        :raises AlreadyVoted: After voting, or when it cannot be told; a
            subclass of ``Unauthorized``.
        """
        if not api.user.has_permission(PERMISSION_VOTE, obj=poll):
            raise Unauthorized
        if self.voted_in_a_poll(poll, request):
            raise AlreadyVoted
        return True

    def anonymous_vote_id(self) -> str:
        """Return a new identifier for an anonymous vote.

        :returns: A random, URL-safe string.
        """
        return secrets.token_urlsafe(16)
