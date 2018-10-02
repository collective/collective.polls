# -*- coding: utf-8 -*-
from collective.polls.config import PROFILE
from collective.polls.testing import INTEGRATION_TESTING
from plone import api

import unittest


class UpgradeTestCaseBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self, from_version, to_version):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.from_version = from_version
        self.to_version = to_version

    def _get_upgrade_step(self, title):
        """Get one of the upgrade steps.

        :param title: [required] the title used to register the upgrade step
        :type obj: str
        """
        self.setup.setLastVersionForProfile(PROFILE, self.from_version)
        upgrades = self.setup.listUpgrades(PROFILE)
        steps = [s for s in upgrades[0] if s['title'] == title]
        return steps[0] if steps else None

    def _do_upgrade_step(self, step):
        """Execute an upgrade step.

        :param step: [required] the step we want to run
        :type step: str
        """
        request = self.layer['request']
        request.form['profile_id'] = PROFILE
        request.form['upgrades'] = [step['id']]
        self.setup.manage_doUpgrades(request=request)

    def _how_many_upgrades_to_do(self):
        self.setup.setLastVersionForProfile(PROFILE, self.from_version)
        upgrades = self.setup.listUpgrades(PROFILE)
        assert len(upgrades) > 0
        return len(upgrades[0])


class Upgrade5to6TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'5', u'6')

    def test_upgrade_to_6_registrations(self):
        version = self.setup.getLastVersionForProfile(PROFILE)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 3)

    def test_register_tasksplease_script(self):
        title = u'Register TasksPlease script'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        script = '++resource++collective.polls/js/jquery.tasksplease.js'
        js_tool = api.portal.get_tool('portal_javascripts')
        js_tool.unregisterResource(script)
        self.assertNotIn(script, js_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertIn(script, js_tool.getResourceIds())

    def test_remove_excanvas_script(self):
        title = u'Remove ExplorerCanvas script'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        script = '++resource++collective.polls/js/excanvas.min.js'
        js_tool = api.portal.get_tool('portal_javascripts')
        js_tool.registerResource(script)
        self.assertIn(script, js_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertNotIn(script, js_tool.getResourceIds())


class Upgrade6to7TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'6', u'7')

    def test_upgrade_to_6_registrations(self):
        version = self.setup.getLastVersionForProfile(PROFILE)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)
