# -*- coding:utf-8 -*-
from five import grok
from zope.interface import implements

from Products.CMFPlone.interfaces import INonInstallable


class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('collective.polls')

    def getNonInstallableProfiles(self):
        profiles = ['collective.polls:uninstall', ]
        return profiles

