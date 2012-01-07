# -*- coding: utf-8 -*-

import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IAttributeUUID

from collective.polls.content.poll import IPoll
from collective.polls.testing import INTEGRATION_TESTING

from collective.polls.config import PERMISSION_VOTE


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_adding(self):
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        p1 = self.folder['p1']
        self.assertTrue(IPoll.providedBy(p1))

    def test_default_values_for_checkboxes(self):
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        p1 = self.folder['p1']
        self.assertTrue(p1.allow_anonymous)
        self.assertTrue(p1.show_results)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        schema = fti.lookupSchema()
        self.assertEquals(IPoll, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.polls.poll')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IPoll.providedBy(new_object))

    def test_is_referenceable(self):
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        p1 = self.folder['p1']
        self.assertTrue(IReferenceable.providedBy(p1))
        self.assertTrue(IAttributeUUID.providedBy(p1))


class VotingTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _set_request_cookies(self, request):
        ''' For each cookie in response, we set a cookie in request '''
        response_cookies = request.response.cookies
        for key, cookie in response_cookies.items():
            request.cookies[key] = cookie['value']

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.setUpPolls()
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def setUpPolls(self):
        self.wt = self.portal.portal_workflow
        wt = self.wt
        # Create 3 polls
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        self.folder.invokeFactory('collective.polls.poll', 'p2')
        self.folder.invokeFactory('collective.polls.poll', 'p3')
        # Set options
        options = [{'option_id':0, 'description':'Option 1'},
                   {'option_id':1, 'description':'Option 2'},
                   {'option_id':2, 'description':'Option 3'},
                  ]
        p1 = self.folder['p1']
        p1.options = options
        p2 = self.folder['p2']
        p2.options = options
        p2.allow_anonymous = False
        p3 = self.folder['p3']
        p3.options = options
        # Open p2 and p3
        wt.doActionFor(self.folder['p2'], 'publish')
        wt.doActionFor(self.folder['p3'], 'publish')
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
        self.assertEqual(self._active_roles(roles),
                         ['Contributor', 'Editor', 'Manager', 'Member',
                          'Reader', 'Reviewer', 'Site Administrator']
                        )

    def test_permission_to_vote_open_poll_anon(self):
        # Poll with allow_anonymous set
        poll = self.p3
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles),
                         ['Anonymous', 'Contributor', 'Editor', 'Manager',
                          'Member', 'Reader', 'Reviewer', 'Site Administrator']
                        )

    def test_permission_to_vote_closed_poll(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wt = self.wt
        poll = self.p3
        wt.doActionFor(poll, 'close')
        roles = poll.rolesOfPermission(PERMISSION_VOTE)
        self.assertEqual(self._active_roles(roles), [])

    def test_vote_closed_poll(self):
        options = 2
        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p1.getResults()
        self.assertEqual(results[options][1], 0)

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

    def test_vote_same_user_twice(self):
        options = 2
        voted = self.p2.setVote(options)
        self.assertTrue(voted)

        self.assertRaises(Unauthorized, self.p1.setVote, options)

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

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p1.getResults()
        self.assertEqual(results[options][1], 0)
        total = self.p1.total_votes
        self.assertEqual(total, 0)

    def test_anonymous_open_restricted_poll(self):
        logout()
        options = 1

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p2.getResults()
        self.assertEqual(results[options][1], 0)
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

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p3.getResults()
        self.assertEqual(results[options][1], 1)
        total = self.p3.total_votes
        self.assertEqual(total, 1)

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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
