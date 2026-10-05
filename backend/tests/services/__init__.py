"""REST services: ``GET @poll``, ``POST @vote``, and polls over ``plone.restapi``.

Functional tests: every request goes through the WSGI publisher, so headers,
cookies, permissions and transaction commits are the real ones.
"""

from collective.polls.config import COOKIE_KEY
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

RESOURCES = Path(__file__).parent.parent / "_resources"
EXAMPLES = RESOURCES / "poll-examples"
SCHEMA = json.loads((RESOURCES / "poll.schema.json").read_text())

__all__ = ["COOKIE_KEY", "EXAMPLES", "OPTIONS", "PASSWORD", "PORTAL_TYPE", "SCHEMA"]
