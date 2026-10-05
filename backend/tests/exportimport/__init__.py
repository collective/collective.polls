"""A closed poll's votes, through plone.exportimport."""

from collective.polls.config import EXPORT_VOTES_KEY
from collective.polls.config import PORTAL_TYPE


OPTIONS = [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"},
    {"option_id": 2, "description": "Maybe"},
]

#: Voter id -> option id, recorded on the polls these tests build.
VOTERS = {"member-a": 0, "member-b": 0, "Anonymous-xyz": 1}

#: What a poll with :data:`VOTERS` exports.
EXPORTED = {
    "counts": {"0": 2, "1": 1},
    "voters": ["Anonymous-xyz", "member-a", "member-b"],
}

__all__ = ["EXPORTED", "EXPORT_VOTES_KEY", "OPTIONS", "PORTAL_TYPE", "VOTERS"]
