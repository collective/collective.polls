"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import logging


__version__ = "3.0.0a1"

PACKAGE_NAME = "collective.polls"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)
