# -*- coding: utf-8 -*-

from collective.polls.content.poll import PollAddForm
from collective.polls.content.poll import PollEditForm
from collective.polls.testing import INTEGRATION_TESTING
from plone import api
from z3c.form import interfaces

import unittest


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

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
