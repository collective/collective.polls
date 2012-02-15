# -*- coding: utf-8 -*-

import unittest2 as unittest

from z3c.form import interfaces

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.polls.content.poll import PollAddForm
from collective.polls.content.poll import PollEditForm

from collective.polls.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_add_form_interface(self):
        context = self.portal
        request = self.request
        add_form = PollAddForm(context, request)
        self.assertTrue(interfaces.IAddForm.providedBy(add_form))

    def test_edit_form_interface(self):
        context = self.portal
        request = self.request
        edit_form = PollEditForm(context, request)
        self.assertTrue(interfaces.IEditForm.providedBy(edit_form))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
