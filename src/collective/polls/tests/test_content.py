# -*- coding: utf-8 -*-

import unittest2 as unittest

from AccessControl import Unauthorized

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.dexterity.interfaces import IDexterityFTI

from collective.polls.content.poll import IPoll
from collective.polls.testing import INTEGRATION_TESTING


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
        self.failUnless(IPoll.providedBy(p1))

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
        self.failUnless(IPoll.providedBy(new_object))


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
        wt = self.portal.portal_workflow
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
        p3 = self.folder['p3']
        p3.options = options
        p3.allow_anonymous = True
        # Open p2 and p3
        wt.doActionFor(self.folder['p2'], 'publish')
        wt.doActionFor(self.folder['p3'], 'publish')
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def test_vote_closed_poll(self):
        options = 2
        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p1.getResults()
        self.failUnless(results[options][1]==0)

    def test_vote_open_poll(self):
        options = 2
        voted = self.p2.setVote(options)
        self.failUnless(voted)
        results = self.p2.getResults()
        self.failUnless(results[options][1]==1)

    def test_vote_same_user_twice(self):
        options = 2
        voted = self.p2.setVote(options)
        self.failUnless(voted)

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p2.getResults()
        self.failUnless(results[options][1]==1)

    def test_invalid_option(self):
        options = 5
        voted = self.p2.setVote(options)
        self.failIf(voted)

        results = self.p2.getResults()
        votes = sum([option[1] for option in results])
        self.failUnless(votes == 0)

    def test_anonymous_closed_poll(self):
        logout()
        options = 1

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p1.getResults()
        self.failUnless(results[options][1]==0)

    def test_anonymous_open_restricted_poll(self):
        logout()
        options = 1

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p2.getResults()
        self.failUnless(results[options][1]==0)

    def test_anonymous_open_poll(self):
        logout()
        options = 1
        voted = self.p3.setVote(options, self.request)
        self.failUnless(voted)
        results = self.p3.getResults()
        self.failUnless(results[options][1]==1)

    def test_anonymous_twice_open_poll(self):
        logout()
        options = 1
        voted = self.p3.setVote(options, self.request)
        self.failUnless(voted)
        self._set_request_cookies(self.request)

        self.assertRaises(Unauthorized, self.p1.setVote, options)

        results = self.p3.getResults()
        self.failUnless(results[options][1]==1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
