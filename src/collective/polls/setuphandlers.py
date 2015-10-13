# -*- coding: utf-8 -*-
from collective.polls.config import PROJECTNAME
from plone import api
from Products.CMFPlone import interfaces as Plone
from Products.CMFQuickInstallerTool import interfaces as QuickInstaller
from zope.interface import implements

import logging

logger = logging.getLogger(PROJECTNAME)


class HiddenProfiles(object):

    implements(Plone.INonInstallable)

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            u'collective.polls:testfixture',
            u'collective.polls:uninstall',
        ]


class HiddenProducts(object):

    implements(QuickInstaller.INonInstallable)

    def getNonInstallableProducts(self):
        """Do not show on QuickInstaller's list of installable products."""
        return [
        ]


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
