# -*- coding:utf-8 -*-
from five import grok
from zope.interface import implements

from Products.CMFPlone.interfaces import INonInstallable


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        profiles = ['collective.polls:uninstall', ]
        return profiles


grok.global_utility(HiddenProfiles,
                    provides=INonInstallable,
                    name="collective.polls")
