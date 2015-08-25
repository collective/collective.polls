# -*- coding: utf-8 -*-

from collective.polls.config import PROJECTNAME
from plone import api


def remove_tile(portal):
    tiles = api.portal.get_registry_record('plone.app.tiles')
    if u'collective.polls' in tiles:
        tiles.remove(u'collective.polls')


def uninstall(portal):
    remove_tile(portal)
    profile = 'profile-%s:uninstall' % PROJECTNAME
    setup_tool = api.portal.get_tool(name='portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile)
    return 'Ran all uninstall steps.'
