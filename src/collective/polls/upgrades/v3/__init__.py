# -*- coding: utf-8 -*-
from collective.polls.config import PROJECTNAME
from collective.polls.logger import logger


def add_poll_tile(setup_tool):
    """Add Poll tile for collective.cover."""
    profile = 'profile-{0}:default'.format(PROJECTNAME)
    setup_tool.runImportStepFromProfile(profile, 'plone.app.registry')
    logger.info('Registry updated.')
