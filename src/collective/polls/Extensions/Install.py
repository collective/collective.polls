# -*- coding: utf-8 -*-

from collective.polls.config import PROJECTNAME
from plone import api


def uninstall(portal):
    profile = 'profile-%s:uninstall' % PROJECTNAME
    setup_tool = api.portal.get_tool(name='portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile)
    return 'Ran all uninstall steps.'
