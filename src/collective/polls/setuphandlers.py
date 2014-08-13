# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from collective.polls.config import PROJECTNAME
from five import grok
from plone import api

import logging

logger = logging.getLogger(PROJECTNAME)


class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('collective.polls')

    def getNonInstallableProfiles(self):
        profiles = ['collective.polls:uninstall', ]
        return profiles


def updateWorkflowDefinitions(portal):
    wf_tool = api.portal.get_tool(name='portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info(u'Workflow definitions updated')


def setupVarious(context):
    if context.readDataFile('collective.polls.marker.txt') is None:
        # not your add-on
        return

    portal = context.getSite()
    updateWorkflowDefinitions(portal)
