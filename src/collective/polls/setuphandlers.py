# -*- coding:utf-8 -*-
from five import grok

from Products.CMFPlone.interfaces import INonInstallable

from Products.CMFCore.utils import getToolByName

class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('collective.polls')

    def getNonInstallableProfiles(self):
        profiles = ['collective.polls:uninstall', ]
        return profiles


def updateWorkflowDefinitions(portal):
    wf_tool = getToolByName(portal, 'portal_workflow')
    wf_tool.updateRoleMappings()
    print "Workflow definitions updated"


def setupVarious(context):
    if context.readDataFile('collective.polls.marker.txt') is None:
        # not your add-on
        return

    portal = context.getSite()
    updateWorkflowDefinitions(portal)