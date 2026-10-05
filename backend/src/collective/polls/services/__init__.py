"""REST services for polls: ``GET @poll`` and ``POST @vote``."""

from collective.polls.content.poll import Poll
from collective.polls.interfaces import ISerializePollState
from collective.polls.interfaces import PollStateDict
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from ZPublisher.HTTPRequest import HTTPRequest


#: For authenticated callers: the answer says whether they voted.
PRIVATE_CACHE_CONTROL = "private, no-store"


class PollService(Service):
    """Base for the poll services.

    Carries an explicit ``__init__`` so the class can be constructed, and
    tested, without the publisher.
    """

    context: Poll

    def __init__(self, context: Poll, request: HTTPRequest) -> None:
        """Bind the service to its poll and request.

        :param context: The poll the service was traversed on.
        :param request: The current request.
        """
        self.context = context
        self.request = request

    def poll_state(self, has_voted: bool | None = None) -> PollStateDict:
        """Return the ``@poll`` payload for this poll and request.

        :param has_voted: Override for ``has_voted``.
        :returns: The payload.
        """
        serializer = getMultiAdapter((self.context, self.request), ISerializePollState)
        return serializer(has_voted=has_voted)
