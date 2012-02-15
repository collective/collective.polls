# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout


from Products.CMFCore.WorkflowCore import WorkflowException

from collective.polls.config import PERMISSION_VOTE

from collective.polls.testing import INTEGRATION_TESTING

ctype = 'collective.polls.poll'
workflow_id = 'poll_workflow'


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _loginAsManager(self):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _transition_poll(self, poll, action):
        self._loginAsManager()
        self.wt.doActionFor(poll, action)

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = getattr(self.portal, 'portal_workflow')
        self.portal_membership = getattr(self.portal, 'portal_membership')
        self.checkPermission = self.portal_membership.checkPermission
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.wt.doActionFor(self.folder, 'publish')

        setRoles(self.portal, TEST_USER_ID, ['Member'])

        self.folder.invokeFactory(ctype, 'obj')
        self.obj = self.folder['obj']

    def test_workflow_installed(self):
        ids = self.wt.getWorkflowIds()
        self.assertTrue(workflow_id in ids)

    def test_default_workflow(self):
        chain = self.wt.getChainForPortalType(self.obj.portal_type)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0], workflow_id)

    def test_workflow_initial_state(self):
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

    def test_workflow_all_stages(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(self.obj, 'submit')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'pending')
        self.wt.doActionFor(self.obj, 'open')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'open')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_anonymous_view_permissions(self):
        checkPermission = self.checkPermission
        logout()
        # Anonymous cannot view a private poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'submit')

        logout()
        # Anonymous cannot view a pending poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'open')

        logout()

        # Anonymous can view an open poll
        self.assertEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'close')
        logout()

        # Anonymous can view a closed poll
        self.assertEqual(checkPermission('View', self.obj), 1)

    def test_workflow_anonymous_view_permissions_private_folder(self):
        folder = self.folder
        # View only to Members in the folder containing our poll
        folder.manage_permission('View', ['Member'], acquire=0)

        checkPermission = self.checkPermission
        logout()
        # Anonymous cannot view a private poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'submit')

        logout()
        # Anonymous cannot view a pending poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'open')

        logout()

        # Anonymous cannot view an open poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

        self._transition_poll(self.obj, 'close')
        logout()

        # Anonymous cannot view a closed poll
        self.assertNotEqual(checkPermission('View', self.obj), 1)

    def test_workflow_anonymous_vote_permissions(self):
        checkPermission = self.checkPermission
        logout()

        # Anonymous cannot vote on a private poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'submit')

        logout()
        # Anonymous cannot vote on a pending poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'open')

        logout()

        # Anonymous can vote on an open poll
        self.assertEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'close')
        logout()

        # Anonymous cannot vote a closed poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

    def test_workflow_anonymous_vote_permissions_private_folder(self):
        folder = self.folder
        # View only to Members in the folder containing our poll
        folder.manage_permission('View', ['Member'], acquire=0)

        checkPermission = self.checkPermission
        logout()

        # Anonymous cannot vote on a private poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'submit')

        logout()
        # Anonymous cannot vote on a pending poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'open')

        logout()

        # Anonymous cannot vote on an open poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

        self._transition_poll(self.obj, 'close')
        logout()

        # Anonymous cannot vote a closed poll
        self.assertNotEqual(checkPermission(PERMISSION_VOTE, self.obj), 1)

    def test_workflow_direct(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wt.doActionFor(self.obj, 'open')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'open')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_transitions_not_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # We cannot close a private poll
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'close')

        self.wt.doActionFor(self.obj, 'submit')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'pending')
        # We cannot close a pending poll
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'close')

        # We can however, retract it
        self.wt.doActionFor(self.obj, 'retract')

        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

        # Let's open it, and try to get it back
        self.wt.doActionFor(self.obj, 'open')

        #Now the poll is opened, we cannot retract, nor submit

        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'retract')

        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'submit')

        # We can however send it back only as a site administrator or manager
        self.wt.doActionFor(self.obj, 'reject')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

        # Finally, let's open it again, so we can close it
        self.wt.doActionFor(self.obj, 'open')
        self.wt.doActionFor(self.obj, 'close')
        review_state = self.wt.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

        #Finally, we cannot do anything else from a closed poll
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'retract')

        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'submit')

        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'open')

    def test_workflow_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # guard-permission: Review portal content
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'open')
        self.wt.doActionFor(self.obj, 'submit')
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'open')

        # Reviewer can retract and open
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.wt.doActionFor(self.obj, 'retract')
        self.wt.doActionFor(self.obj, 'open')

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # Now, only Manager, Site Administrator and Reviewer can
        # close the poll
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'close')

        setRoles(self.portal, TEST_USER_ID, ['Owner',
                                             'Member',
                                             'Contributor',
                                             'Editor'])
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'close')

        # Now, only Site Administrator, Manager, Reviewer can send it back
        setRoles(self.portal, TEST_USER_ID, ['Owner',
                                             'Member',
                                             'Editor',
                                             'Contributor'])
        self.assertRaises(WorkflowException,
                          self.wt.doActionFor,
                          self.obj, 'reject')

        # Reviewer can send the poll back
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.wt.doActionFor(self.obj, 'reject')

        # Finally, let's get Reviewer role, and open and close
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.wt.doActionFor(self.obj, 'open')
        self.wt.doActionFor(self.obj, 'close')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
