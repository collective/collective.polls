# -*- coding: utf-8 -*-

from collective.polls.config import PROJECTNAME
from plone import api


def remove_tile():
    tiles = api.portal.get_registry_record('plone.app.tiles')
    if u'collective.polls' in tiles:
        tiles.remove(u'collective.polls')


def uninstall(portal, reinstall=False):
    if not reinstall:
        remove_tile()
        profile = 'profile-{0}:uninstall'.format(PROJECTNAME)
        setup_tool = api.portal.get_tool('portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        return 'Ran all uninstall steps.'
