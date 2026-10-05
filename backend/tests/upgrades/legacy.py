"""Build polls holding their votes exactly as 2.x stored them.

2.x kept the voter ids in a plain list under ``voters_members_id`` and one
``int`` per option under ``option.%02d``, keyed by the option's position.
Its ``options`` field held a list of ``{option_id, description}`` dicts.
"""

from . import PORTAL_TYPE
from collective.polls.content.poll import Poll
from plone import api
from plone.dexterity.content import DexterityContent
from random import Random
from typing import Any
from zope.annotation.interfaces import IAnnotations


VOTERS_KEY = "voters_members_id"
COUNT_KEY = "option.%02d"


def make_legacy_poll(
    container: DexterityContent,
    poll_id: str,
    options: list[Any],
    voters: list[str],
    counts: dict[int, int],
) -> Poll:
    """Create an open poll and give it 2.x options and votes.

    The options are written after creation, so the 3.0 subscriber that
    gives options ids does not see them, as on a site not yet upgraded.

    :param container: Where to create the poll.
    :param poll_id: Its id.
    :param options: The ``options`` value to store, as 2.x had it.
    :param voters: The ``voters_members_id`` list.
    :param counts: Option id to count; one ``option.%02d`` key each.
    :returns: The poll.
    """
    with api.env.adopt_roles(["Manager"]):
        poll = api.content.create(
            container,
            PORTAL_TYPE,
            poll_id,
            options=[{"description": "A"}, {"description": "B"}],
        )
        api.content.transition(obj=poll, transition="open")
    poll.options = options
    annotations = IAnnotations(poll)
    annotations[VOTERS_KEY] = list(voters)
    for option_id, count in counts.items():
        annotations[COUNT_KEY % option_id] = count
    return poll


def random_legacy_votes(
    seed: int,
) -> tuple[list[dict[str, Any]], list[str], dict[int, int]]:
    """Return 2.x options, voters and counts drawn from a seed.

    Some options have no count key at all, as 2.x wrote one only on the
    first vote; some voters repeat, as nothing stopped it.

    :param seed: The random seed.
    :returns: ``(options, voters, counts)``.
    """
    rnd = Random(seed)  # noqa: S311
    size = rnd.randint(2, 6)
    options = [{"option_id": i, "description": f"Option {i}"} for i in range(size)]
    counts = {i: rnd.randint(1, 30) for i in range(size) if rnd.random() < 0.8}
    members = [f"member-{i}" for i in range(rnd.randint(0, 10))]
    anonymous = [f"Anonymous-{rnd.randint(10**9, 10**10)}" for _ in range(5)]
    voters = members + anonymous
    voters += rnd.sample(voters, k=min(2, len(voters)))
    rnd.shuffle(voters)
    return options, voters, counts
