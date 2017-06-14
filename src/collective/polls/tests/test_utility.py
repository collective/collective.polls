# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.polls.polls import IPolls
from collective.polls.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import logout
from plone.uuid.interfaces import IUUID
from zope.component import queryUtility

import unittest


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = self.portal.portal_workflow

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')
            api.content.transition(obj=self.folder, transition='publish')
            self.subfolder = api.content.create(self.folder, 'Folder',
                                                'folder')
            api.content.transition(obj=self.subfolder, transition='publish')
            self.setUpPolls()

    def setUpPolls(self):
        wt = self.wt
        # Create 6 polls
        self.folder.invokeFactory('collective.polls.poll', 'p1')
        self.folder.invokeFactory('collective.polls.poll', 'p2')
        self.folder.invokeFactory('collective.polls.poll', 'p3')
        self.subfolder.invokeFactory('collective.polls.poll', 'p4')
        self.subfolder.invokeFactory('collective.polls.poll', 'p5')
        self.subfolder.invokeFactory('collective.polls.poll', 'p6')
        # Open 2 polls
        wt.doActionFor(self.folder['p2'], 'open')
        wt.doActionFor(self.subfolder['p5'], 'open')

    def test_utility_registered(self):
        """Test if our utility was properly registered."""
        utility = queryUtility(IPolls, name='collective.polls')
        self.assertTrue(IPolls.providedBy(utility))

    def test_recent_polls(self):
        """List 5 recent polls, including closed ones."""
        utility = queryUtility(IPolls, name='collective.polls')
        polls = utility.recent_polls(show_all=True)
        self.assertEqual(len(polls), 5)

    def test_recent_polls_expand_limit(self):
        """List all recent polls, including closed ones."""
        utility = queryUtility(IPolls, name='collective.polls')
        polls = utility.recent_polls(show_all=True, limit=10)
        self.assertEqual(len(polls), 6)

    def test_open_recent_polls(self):
        """List open recent polls."""
        utility = queryUtility(IPolls, name='collective.polls')
        polls = utility.recent_polls(show_all=False)
        self.assertEqual(len(polls), 2)

    def test_polls_context(self):
        """List for polls in subfolder context."""
        utility = queryUtility(IPolls, name='collective.polls')
        context = self.subfolder
        polls = utility.recent_polls(context=context, show_all=True)
        self.assertEqual(len(polls), 3)

    def test_open_polls_context(self):
        """List for open polls in subfolder context."""
        utility = queryUtility(IPolls, name='collective.polls')
        context = self.subfolder
        polls = utility.recent_polls(context=context, show_all=False)
        self.assertEqual(len(polls), 1)

    def test_poll_by_uid(self):
        """Get poll for a given UID."""
        base_poll = self.subfolder['p5']
        uid = IUUID(base_poll)
        utility = queryUtility(IPolls, name='collective.polls')
        poll = utility.poll_by_uid(uid=uid)
        self.assertEqual(poll, base_poll)

    def test_latest_poll(self):
        """Get poll the latest open poll."""
        base_poll = self.subfolder['p5']
        uid = 'latest'
        utility = queryUtility(IPolls, name='collective.polls')
        poll = utility.poll_by_uid(uid=uid)
        self.assertEqual(poll, base_poll)

    def test_voted_in_a_poll(self):
        """Test if a user voted in a poll."""
        utility = queryUtility(IPolls, name='collective.polls')
        poll = self.subfolder['p5']
        poll.options = [{'option_id': 0, 'description': 'Option 1'}, ]
        self.assertFalse(utility.voted_in_a_poll(poll))
        # Vote in a poll
        poll.setVote(0)
        self.assertTrue(utility.voted_in_a_poll(poll))

    def test_error_voted_in_a_poll(self):
        """Test if a user voted in a poll."""
        logout()
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, allowed to vote
        poll = self.subfolder['p5']
        # Anonymous user and we do not pass a request
        self.assertTrue(utility.voted_in_a_poll(poll))

    def test_allowed_to_vote(self):
        """Test if a user voted in a poll."""
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, allowed to vote
        poll = self.subfolder['p5']
        self.assertTrue(utility.allowed_to_vote(poll))
        # Unpuclished poll, not allowed to vote
        poll = self.subfolder['p6']

        with self.assertRaises(Unauthorized):
            utility.allowed_to_vote(poll)

    def test_allowed_to_view(self):
        """Member can view a opened poll."""
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, member can view
        poll = self.subfolder['p5']
        self.assertTrue(utility.allowed_to_view(poll))

    def test_allowed_to_edit(self):
        """Test if member can edit a poll."""
        utility = queryUtility(IPolls, name='collective.polls')
        # Private Poll, member can edit
        poll = self.subfolder['p6']
        self.assertTrue(utility.allowed_to_edit(poll))

    def test_not_allowed_to_edit(self):
        """Test if member can edit a poll."""
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, member cannot edit
        poll = self.subfolder['p5']
        self.assertFalse(utility.allowed_to_edit(poll))

    def test_anonymous_allowed_to_view(self):
        """Anonymous can view a opened poll."""
        logout()
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, member can view
        poll = self.subfolder['p5']
        self.assertTrue(utility.allowed_to_view(poll))

    def test_anonymous_not_allowed_to_view(self):
        """Anonymous cannot view a private poll."""
        logout()
        utility = queryUtility(IPolls, name='collective.polls')
        # Opened Poll, member can view
        poll = self.subfolder['p6']
        self.assertFalse(utility.allowed_to_view(poll))
