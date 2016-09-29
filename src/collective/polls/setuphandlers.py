# -*- coding: utf-8 -*-
from collective.polls.logger import logger
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            u'collective.polls:testfixture',
            u'collective.polls:uninstall',
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
