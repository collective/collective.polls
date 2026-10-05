"""REST services: ``GET @poll``, ``POST @vote``, and polls over ``plone.restapi``.

Functional tests: every request goes through the WSGI publisher, so headers,
cookies, permissions and transaction commits are the real ones.
"""

from collective.polls.config import COOKIE_KEY
from collective.polls.config import EXPORT_VOTES_KEY
from collective.polls.config import PORTAL_TYPE
from pathlib import Path

import json


#: Password of every member these tests create.
PASSWORD = "secret-password-123"  # noqa: S105

#: The options of every poll these tests create.
OPTIONS = [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"},
]

#: The options of the multiple choice polls these tests create.
THREE_OPTIONS = [
    {"option_id": 0, "description": "Red"},
    {"option_id": 1, "description": "Green"},
    {"option_id": 2, "description": "Blue"},
]

RESOURCES = Path(__file__).parent.parent / "_resources"
EXAMPLES = RESOURCES / "poll-examples"
SCHEMA = json.loads((RESOURCES / "poll.schema.json").read_text())

__all__ = [
    "COOKIE_KEY",
    "EXAMPLES",
    "EXPORT_VOTES_KEY",
    "OPTIONS",
    "PASSWORD",
    "PORTAL_TYPE",
    "SCHEMA",
    "THREE_OPTIONS",
]
