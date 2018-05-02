# -*- coding: utf-8 -*-
from collective.polls.config import IS_PLONE_5
from collective.polls.config import PROFILE
from collective.polls.config import PROJECTNAME
from collective.polls.testing import INTEGRATION_TESTING
from collective.polls.testing import IS_BBB
from collective.polls.testing import QIBBB

import unittest


JS = (
    '++resource++collective.polls/js/jquery.flot.js',
    '++resource++collective.polls/js/jquery.flot.pie.js',
    '++resource++collective.polls/js/polls.js',
    '++resource++collective.polls/js/collective.poll.js',
    '++resource++collective.polls/js/jquery.tasksplease.js',
)

CSS = (
    '++resource++collective.polls/css/collective.polls.css',
)


class InstallTestCase(unittest.TestCase, QIBBB):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    @unittest.skipIf(IS_BBB, 'Plone >= 5.1')
    def test_installed(self):
        from Products.CMFPlone.utils import get_installer
        qi = get_installer(self.portal, self.request)
        self.assertTrue(qi.is_product_installed(PROJECTNAME))

    @unittest.skipUnless(IS_BBB, 'Plone < 5.1')
    def test_installed_BBB(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_profile_version(self):
        setup_tool = self.portal['portal_setup']
        self.assertEqual(
            setup_tool.getLastVersionForProfile(PROFILE), (u'6',))

    def test_add_permission(self):
        permission = 'collective.polls: Add poll'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertEqual(
            roles, ['Contributor', 'Manager', 'Owner', 'Site Administrator'])

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

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for js in JS:
            self.assertIn(js, resource_ids, '{0} not installed'.format(js))

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for css in CSS:
            self.assertIn(css, resource_ids, '{0} not installed'.format(css))


class UninstallTestCase(unittest.TestCase, QIBBB):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.qi = self.uninstall()  # BBB: QI compatibility

    @unittest.skipIf(IS_BBB, 'Plone >= 5.1')
    def test_uninstalled(self):
        self.assertFalse(self.qi.is_product_installed(PROJECTNAME))

    @unittest.skipUnless(IS_BBB, 'Plone < 5.1')
    def test_uninstalled_BBB(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for js in JS:
            self.assertNotIn(js, resource_ids, '{0} not installed'.format(js))

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for css in CSS:
            self.assertNotIn(css, resource_ids, '{0} not installed'.format(css))
