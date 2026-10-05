"""A vote fires a purge event, so caching proxies drop the stale poll."""

from z3c.caching.interfaces import IPurgeable
from z3c.caching.interfaces import IPurgeEvent
from zope.component import eventtesting


def test_poll_is_purgeable(polls):
    assert IPurgeable.providedBy(polls["p2"])


def test_vote_fires_purge(polls):
    eventtesting.setUp()
    polls["p2"].setVote(0)
    purged = [e for e in eventtesting.getEvents() if IPurgeEvent.providedBy(e)]
    assert purged
    assert all(e.object is polls["p2"] for e in purged)
