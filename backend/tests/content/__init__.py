"""The Poll content type: FTI, schema, voting, deletion.

Shared values live here so the modules import them relatively.
"""

from collective.polls.config import PORTAL_TYPE


#: The options the legacy voting tests used.
OPTIONS = [
    {"option_id": 0, "description": "Option 1"},
    {"option_id": 1, "description": "Option 2"},
    {"option_id": 2, "description": "Option 3"},
]

__all__ = ["OPTIONS", "PORTAL_TYPE"]
