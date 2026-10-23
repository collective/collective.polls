"""The upgrades from 2.x to 3000, and on to the current version."""

from collective.polls.config import PORTAL_TYPE


PROFILE = "collective.polls:default"

#: Profile version of the last 2.x code.
SOURCE = "7"

DESTINATION = "3000"

#: Profile version of the current code.
LATEST = "3001"

__all__ = ["DESTINATION", "LATEST", "PORTAL_TYPE", "PROFILE", "SOURCE"]
