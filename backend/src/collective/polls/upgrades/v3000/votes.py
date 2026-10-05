"""Move votes from the 2.x annotations to the 3.0 storage."""

from collections.abc import Iterator
from collective.polls import logger
from collective.polls.config import PORTAL_TYPE
from collective.polls.content.poll import Poll
from collective.polls.interfaces import IPollVotes
from collective.polls.options import normalize_options
from plone import api
from Products.GenericSetup.tool import SetupTool
from typing import Any
from zope.annotation.interfaces import IAnnotations

import re
import transaction


#: 2.x annotation holding the list of voter ids. Only this module knows it.
LEGACY_VOTERS_KEY = "voters_members_id"

#: 2.x annotations holding one count per option id: ``option.00``, …
LEGACY_COUNT_KEY = re.compile(r"^option\.(\d+)$")

#: Polls handled between savepoints.
BATCH_SIZE = 100


class MigrationError(RuntimeError):
    """The migrated votes of a poll do not add up to the 2.x ones."""


def all_polls() -> Iterator[Poll]:
    """Yield every poll of the site, whoever may see it.

    Takes a savepoint every :data:`BATCH_SIZE` polls.

    :returns: An iterator over the polls.
    """
    # plone-stubs declares the catalog's search methods as returning None.
    catalog: Any = api.portal.get_tool("portal_catalog")
    brains = catalog.unrestrictedSearchResults(portal_type=PORTAL_TYPE)
    for index, brain in enumerate(brains, start=1):
        yield brain._unrestrictedGetObject()
        if index % BATCH_SIZE == 0:
            transaction.savepoint(optimistic=True)


def legacy_keys(poll: Poll) -> list[str]:
    """Return the 2.x vote annotation keys a poll holds.

    :param poll: The poll.
    :returns: The keys, possibly none.
    """
    return [
        key
        for key in IAnnotations(poll)
        if isinstance(key, str)
        and (key == LEGACY_VOTERS_KEY or LEGACY_COUNT_KEY.match(key))
    ]


def legacy_votes(poll: Poll, keys: list[str]) -> tuple[list[str], dict[int, int]]:
    """Read the 2.x votes of a poll.

    :param poll: The poll.
    :param keys: Its 2.x vote annotation keys, from :func:`legacy_keys`.
    :returns: The voter ids, without repeats, and the count per option id.
    """
    annotations = IAnnotations(poll)
    counts: dict[int, int] = {}
    for key in keys:
        match = LEGACY_COUNT_KEY.match(key)
        if match:
            option_id = int(match.group(1))
            counts[option_id] = counts.get(option_id, 0) + int(annotations[key])
    voters = list(dict.fromkeys(annotations.get(LEGACY_VOTERS_KEY, [])))
    return voters, counts


def _normalize(poll: Poll) -> None:
    """Give every option of a poll an id, the way 2.x numbered them.

    2.x numbered options by position, so a poll whose options have no ids
    gets ``0, 1, 2…``, which is what its stored counts refer to.

    :param poll: The poll.
    """
    options = poll.options or []
    if all(isinstance(o, dict) and "option_id" in o for o in options):
        return
    poll.options = normalize_options(options)
    logger.info("%s: gave its options ids", poll.absolute_url(1))


def migrate_poll(poll: Poll) -> bool:
    """Move the 2.x votes of one poll to the 3.0 storage.

    Votes already in the 3.0 storage, cast before the upgrade ran, are
    kept and the 2.x ones are added to them. The result is checked before
    the 2.x data is deleted.

    :param poll: The poll.
    :returns: ``True`` when the poll had 2.x votes to move.
    :raises MigrationError: When the stored votes do not add up.
    """
    keys = legacy_keys(poll)
    if not keys:
        return False
    voters, counts = legacy_votes(poll, keys)
    _normalize(poll)
    votes = IPollVotes(poll)
    before_voters = set(votes.voters())
    before_total = sum(votes.counts().values()) + sum(votes.orphans().values())
    votes.merge(counts, voters)
    after_total = sum(votes.counts().values()) + sum(votes.orphans().values())
    if after_total != before_total + sum(counts.values()):
        raise MigrationError(f"{poll.absolute_url(1)}: vote counts do not add up")
    if set(votes.voters()) != before_voters | set(voters):
        raise MigrationError(f"{poll.absolute_url(1)}: voters do not match")
    annotations = IAnnotations(poll)
    for key in keys:
        del annotations[key]
    orphans = votes.orphans()
    if orphans:
        logger.warning(
            "%s: votes for options it no longer has: %s",
            poll.absolute_url(1),
            orphans,
        )
    logger.info(
        "%s: moved %d votes from %d voters",
        poll.absolute_url(1),
        sum(counts.values()),
        len(voters),
    )
    return True


def migrate_votes(setup_tool: SetupTool) -> None:
    """Move the votes of every poll to the 3.0 storage.

    :param setup_tool: The ``portal_setup`` tool.
    """
    migrated = skipped = 0
    for poll in all_polls():
        if migrate_poll(poll):
            migrated += 1
        else:
            skipped += 1
    logger.info("Votes: %d polls migrated, %d had nothing to move", migrated, skipped)
