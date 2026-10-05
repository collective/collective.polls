"""Keep the ids of a poll's options stable, whoever wrote them.

The REST API, ``plone.api`` and content imports all store ``options`` as
they received it. Normalizing on add and on modify gives every new option
an id in one place, whichever way it arrived.
"""

from collective.polls.content.poll import Poll
from collective.polls.options import normalize_options
from zope.interface.interfaces import IObjectEvent


def normalize_poll_options(poll: Poll, event: IObjectEvent) -> None:
    """Give every option of a poll an id, writing only when something changed.

    A vote fires ``ObjectModifiedEvent`` too, so this runs on every vote; it
    must not write then, or every vote would rewrite the poll.

    :param poll: The poll added or modified.
    :param event: The lifecycle event.
    """
    current = poll.options
    normalized = normalize_options(current)
    if normalized != current:
        poll.options = normalized
