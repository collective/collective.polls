"""``GET @poll``."""

from collective.polls.interfaces import PollStateDict
from collective.polls.services import PollService
from collective.polls.services import PRIVATE_CACHE_CONTROL
from plone import api


#: For anonymous callers, as the 2.x results view answered: browsers always
#: revalidate, shared caches keep the answer for two minutes.
PUBLIC_CACHE_CONTROL = "max-age=0, s-maxage=120"


def etag_matches(header: str, etag: str) -> bool:
    """Check an ``If-None-Match`` header against an entity tag.

    :param header: The header value: ``*``, or a comma separated list of
        tags, strong or weak (``W/``), quoted or not.
    :param etag: The current entity tag, quoted.
    :returns: ``True`` when the header names the tag, or is ``*``.
    """
    wanted = etag.strip('"')
    for tag in header.split(","):
        tag = tag.strip().removeprefix("W/").strip('"')
        if tag in ("*", wanted):
            return True
    return False


class PollGet(PollService):
    """Answer the state of a poll."""

    def etag(self) -> str:
        """Return the entity tag of the anonymous answer.

        Votes change ``modified``; workflow transitions may not, and they
        change what the answer says, so the state is part of the tag.

        :returns: A quoted entity tag.
        """
        modified = self.context.modified().timeTime()
        state = api.content.get_state(self.context)
        return f'"{modified}-{state}"'

    def reply(self) -> PollStateDict | object:
        """Return the state of the poll, as seen by the current user.

        Anonymous answers are the same for every visitor, so they carry an
        entity tag and may be cached by shared caches; a matching
        ``If-None-Match`` gets ``304`` with no body. Answers to members say
        whether they voted, so they are private.

        :returns: The ``@poll`` payload, or no content for a ``304``.
        """
        response = self.request.response
        if not api.user.is_anonymous():
            response.setHeader("Cache-Control", PRIVATE_CACHE_CONTROL)
            return self.poll_state()
        etag = self.etag()
        response.setHeader("Cache-Control", PUBLIC_CACHE_CONTROL)
        response.setHeader("ETag", etag)
        if etag_matches(self.request.getHeader("If-None-Match", ""), etag):
            return self.reply_no_content(status=304)
        return self.poll_state()
