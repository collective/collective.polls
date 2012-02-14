# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.polls.config import PROJECTNAME
from collective.polls.testing import INTEGRATION_TESTING

JAVASCRIPTS = [
    "++resource++collective.polls/js/raphael-min.js",
    "++resource++collective.polls/js/g.raphael-min.js",
    "++resource++collective.polls/js/g.pie-min.js",
    "++resource++collective.polls/js/g.bar-min.js",
    "++resource++collective.polls/js/collective.poll.js",
    ]


class InstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_add_permission(self):
        permission = 'collective.polls: Add poll'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertEqual(roles, ['Contributor', 'Manager', 'Owner',
                                 'Site Administrator'])

    def test_vote_permission(self):
        permission = 'collective.polls: Vote'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertEqual(roles, [])

    def test_close_permission(self):
        permission = 'collective.polls: Close poll'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertEqual(roles, ['Manager', 'Reviewer', 'Site Administrator'])

    def test_jsregistry(self):
        portal_javascripts = self.portal.portal_javascripts
        for js in JAVASCRIPTS:
            self.assertTrue(js in portal_javascripts.getResourceIds(),
                            '%s not installed' % js)


class UninstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_jsregistry_removed(self):
        portal_javascripts = self.portal.portal_javascripts
        for js in JAVASCRIPTS:
            self.assertFalse(js in portal_javascripts.getResourceIds(),
                             '%s not removed' % js)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
