# -*- coding: utf-8 -*-
from collective.polls.testing import INTEGRATION_TESTING
from plone import api

import unittest


class ViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        with api.env.adopt_roles(['Manager']):
            self.poll = api.content.create(
                self.portal, 'collective.polls.poll', 'poll')


class UpdatePollViewTestCase(ViewTestCase):

    def render(self):
        view = api.content.get_view('update-poll', self.poll, self.request)
        view()

    def test_headers_no_match(self):
        last_modified = str(self.poll.modified().timeTime())
        self.render()

        headers = self.request.response.headers
        self.assertEqual(self.request.response.getStatus(), 200)
        self.assertEqual(headers['cache-control'], 'max-age=0, s-maxage=120')
        self.assertEqual(headers['etag'], last_modified)

    def test_headers_match(self):
        last_modified = str(self.poll.modified().timeTime())
        self.request.environ['IF_NONE_MATCH'] = last_modified
        self.render()

        headers = self.request.response.headers
        self.assertEqual(self.request.response.getStatus(), 304)
        self.assertEqual(headers['cache-control'], 'max-age=0, s-maxage=120')
        self.assertEqual(headers['etag'], last_modified)

    def test_non_safe_method(self):
        self.request.environ['REQUEST_METHOD'] = 'PUT'
        self.render()

        self.assertEqual(self.request.response.getStatus(), 412)
