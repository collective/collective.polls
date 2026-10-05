"""Vote storage: ``IPollVotes`` and the BTrees behind it."""

from collective.polls.config import PORTAL_TYPE
from collective.polls.config import VOTES_ANNO_KEY


OPTIONS = [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"},
    {"option_id": 2, "description": "Maybe"},
]

__all__ = ["OPTIONS", "PORTAL_TYPE", "VOTES_ANNO_KEY"]
