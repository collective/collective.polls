"""Workflow subscribers: the anonymous grant on open, clearing votes on reject."""

from collective.polls.config import PERMISSION_VOTE
from collective.polls.config import PORTAL_TYPE


OPTIONS = [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"},
]

__all__ = ["OPTIONS", "PERMISSION_VOTE", "PORTAL_TYPE"]
