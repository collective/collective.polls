"""Installing and uninstalling the add-on.

Shared values live here so the modules import them relatively.
"""

from collective.polls import PACKAGE_NAME


PROFILE = f"{PACKAGE_NAME}:default"

#: Version of the default profile; bump it together with metadata.xml.
PROFILE_VERSION = "3000"

ADD_POLL = "collective.polls: Add poll"
CLOSE_POLL = "collective.polls: Close poll"
VOTE = "collective.polls: Vote"
