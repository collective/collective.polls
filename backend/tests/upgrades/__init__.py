"""The upgrade from 2.x to 3000."""

from collective.polls.config import PORTAL_TYPE


PROFILE = "collective.polls:default"

#: Profile version of the last 2.x code.
SOURCE = "7"

DESTINATION = "3000"

__all__ = ["DESTINATION", "PORTAL_TYPE", "PROFILE", "SOURCE"]
