# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.polls.config import PERMISSION_VOTE
from collective.polls.content.poll import InsuficientOptions
from collective.polls.content.poll import IPoll
from collective.polls.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class MockPoll(object):
    options = []


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

        self.poll = api.content.create(
            self.folder, 'collective.polls.poll', 'poll')

    def test_adding(self):
        self.assertTrue(IPoll.providedBy(self.poll))

    def test_default_values_for_checkboxes(self):
        self.assertTrue(self.poll.allow_anonymous)
        self.assertTrue(self.poll.show_results)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        self.assertIsNotNone(fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        schema = fti.lookupSchema()
        self.assertEqual(IPoll, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IPoll.providedBy(new_object))

    def test_validate_no_options(self):
        data = MockPoll()

        with self.assertRaises(InsuficientOptions):
            IPoll.validateInvariants(data)

    def test_validate_one_option(self):
        data = MockPoll()
        data.options = [{'option_id': 0, 'description': 'Foo'}]

        with self.assertRaises(InsuficientOptions):
            IPoll.validateInvariants(data)

    def test_validate_two_options(self):
        data = MockPoll()
        data.options = [
            {'option_id': 0, 'description': 'Foo'},
            {'option_id': 1, 'description': 'Bar'},
        ]
        try:
            IPoll.validateInvariants(data)
        except InsuficientOptions:
            self.fail()


class VotingTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _set_request_cookies(self, request):
        """For each cookie in response, we set a cookie in request."""
        response_cookies = request.response.cookies
        for key, cookie in response_cookies.items():
            request.cookies[key] = cookie['value']

    def reject_poll(self, poll):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(poll, 'reject')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        logout()

    def open_poll(self, poll):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(poll, 'open')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        logout()

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')
            self.wt = self.portal.portal_workflow
            self.wt.doActionFor(self.folder, 'publish')
            self.setUpPolls()

    def setUpPolls(self):
        wt = self.wt
        # Create 3 polls
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        self.folder.invokeFactory('collective.polls.poll', 'p2')
        self.folder.invokeFactory('collective.polls.poll', 'p3')
        # Set options
        options = [
            {'option_id': 0, 'description': 'Option 1'},
            {'option_id': 1, 'description': 'Option 2'},
            {'option_id': 2, 'description': 'Option 3'},
        ]
        p1 = self.folder['p1']
        p1.options = options
        p2 = self.folder['p2']
        p2.options = options
        p2.allow_anonymous = False
        p3 = self.folder['p3']
        p3.options = options
        # Open p2 and p3
        wt.doActionFor(self.folder['p2'], 'open')
        wt.doActionFor(self.folder['p3'], 'open')
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def _active_roles(self, roles):
        return [r['name'] for r in roles if r['selected']]

    def test_permission_to_vote_private_poll(self):
        poll = self.p1
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [])

    def test_permission_to_vote_pending_poll(self):
        wt = self.wt
        poll = self.p1
        wt.doActionFor(poll, 'submit')
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [])

    def test_permission_to_vote_open_poll(self):
        # Poll without allow_anonymous set
        poll = self.p2
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [
            'Contributor',
            'Editor',
            'Manager',
            'Member',
            'Reader',
            'Reviewer',
            'Site Administrator',
        ])

    def test_permission_to_vote_open_poll_anon(self):
        # Poll with allow_anonymous set
        poll = self.p3
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [
            'Anonymous',
            'Contributor',
            'Editor',
            'Manager',
            'Member',
            'Reader',
            'Reviewer',
            'Site Administrator',
        ])

    def test_permission_to_vote_closed_poll(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wt = self.wt
        poll = self.p3
        wt.doActionFor(poll, 'close')
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [])

    def test_vote_closed_poll(self):
        options = 2

        with self.assertRaises(Unauthorized):
            self.p1.setVote(options)

        results = self.p1.getResults()
        self.assertEqual(results, [])

        total = self.p1.total_votes
        self.assertEqual(total, 0)

    def test_vote_open_poll(self):
        options = 2
        voted = self.p2.setVote(options)
        self.assertTrue(voted)
        results = self.p2.getResults()
        self.assertEqual(results[options][1], 1)
        total = self.p2.total_votes
        self.assertEqual(total, 1)

    def test_vote_open_poll_reject_vote_again(self):
        options = 2
        wt = self.wt
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Reviewer'])
        self.p2.setVote(options)
        self.assertEqual(self.p2.total_votes, 1)
        # Send poll back, must erase votes
        wt.doActionFor(self.p2, 'reject')
        self.assertEqual(self.p2.total_votes, 0)
        # Open again
        wt.doActionFor(self.p2, 'open')
        # User must be allowed to vote again
        self.p2.setVote(options)
        self.assertEqual(self.p2.total_votes, 1)

    def test_vote_same_user_twice(self):
        options = 2
        voted = self.p2.setVote(options)
        self.assertTrue(voted)

        with self.assertRaises(Unauthorized):
            self.p1.setVote(options)

        results = self.p2.getResults()
        self.assertEqual(results[options][1], 1)
        total = self.p2.total_votes
        self.assertEqual(total, 1)

    def test_invalid_option(self):
        options = 5
        voted = self.p2.setVote(options)
        self.assertFalse(voted)

        total = self.p2.total_votes
        self.assertEqual(total, 0)

    def test_anonymous_closed_poll(self):
        logout()
        options = 1

        with self.assertRaises(Unauthorized):
            self.p1.setVote(options)

        results = self.p1.getResults()
        self.assertEqual(results, [])
        total = self.p1.total_votes
        self.assertEqual(total, 0)

    def test_anonymous_open_restricted_poll(self):
        logout()
        options = 1

        with self.assertRaises(Unauthorized):
            self.p1.setVote(options)

        results = self.p2.getResults()
        self.assertEqual(results, [])
        total = self.p2.total_votes
        self.assertEqual(total, 0)

    def test_anonymous_open_poll(self):
        logout()
        options = 1
        voted = self.p3.setVote(options, self.request)
        self.assertTrue(voted)
        results = self.p3.getResults()
        self.assertEqual(results[options][1], 1)
        total = self.p3.total_votes
        self.assertEqual(total, 1)

    def test_anonymous_twice_open_poll(self):
        logout()
        options = 1
        voted = self.p3.setVote(options, self.request)
        self.assertTrue(voted)
        self._set_request_cookies(self.request)

        with self.assertRaises(Unauthorized):
            self.p3.setVote(*(options, self.request))

        results = self.p3.getResults()
        self.assertEqual(results[options][1], 1)
        total = self.p3.total_votes
        self.assertEqual(total, 1)

    def test_anonymous_vote_after_reopen_poll(self):
        logout()
        options = 1
        # Anonymous user can vote
        voted = self.p3.setVote(options, self.request)
        self.assertTrue(voted)
        self._set_request_cookies(self.request)
        # Reject the poll
        self.reject_poll(self.p3)
        # Reopen the poll
        self.open_poll(self.p3)
        # Anonymous user can vote again
        voted = self.p3.setVote(options, self.request)
        self.assertTrue(voted)

    def test_percentage_vote_report(self):
        poll = self.p3
        # Vote as logged user
        options = 2
        voted = poll.setVote(options, self.request)
        self.assertTrue(voted)

        total = poll.total_votes
        self.assertEqual(total, 1)

        results = poll.getResults()
        # One vote
        self.assertEqual(results[options][1], 1)
        # 100%
        self.assertEqual(results[options][2], 1.0)

        logout()
        options = 1
        voted = poll.setVote(options, self.request)
        self.assertTrue(voted)

        total = poll.total_votes
        self.assertEqual(total, 2)

        results = poll.getResults()
        # One vote
        self.assertEqual(results[options][1], 1)
        # 50%
        self.assertEqual(results[options][2], 0.5)
