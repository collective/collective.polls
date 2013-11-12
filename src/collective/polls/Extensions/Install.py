# -*- coding: utf-8 -*-

from collective.polls.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName


def uninstall(portal):
    profile = 'profile-%s:uninstall' % PROJECTNAME
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile)
    return "Ran all uninstall steps."
