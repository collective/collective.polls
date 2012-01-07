# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from Products.CMFCore.WorkflowCore import WorkflowException

from collective.polls.testing import INTEGRATION_TESTING

ctype = 'collective.polls.poll'
workflow_id = 'poll_workflow'


class WorkflowTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.workflow_tool = getattr(self.portal, 'portal_workflow')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

        self.folder.invokeFactory(ctype, 'obj')
        self.obj = self.folder['obj']

    def test_workflow_installed(self):
        ids = self.workflow_tool.getWorkflowIds()
        self.assertTrue(workflow_id in ids)

    def test_default_workflow(self):
        chain = self.workflow_tool.getChainForPortalType(self.obj.portal_type)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0], workflow_id)

    def test_workflow_initial_state(self):
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

    def test_workflow_all_stages(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.workflow_tool.doActionFor(self.obj, 'submit')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'pending')
        self.workflow_tool.doActionFor(self.obj, 'publish')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'open')
        self.workflow_tool.doActionFor(self.obj, 'close')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_direct(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.workflow_tool.doActionFor(self.obj, 'publish')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'open')
        self.workflow_tool.doActionFor(self.obj, 'close')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

    def test_workflow_transitions_not_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # We cannot close a private poll
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'close')

        self.workflow_tool.doActionFor(self.obj, 'submit')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'pending')
        # We cannot close a pending poll
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'close')

        # We can however, retract it
        self.workflow_tool.doActionFor(self.obj, 'retract')

        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

        # Let's open it, and try to get it back
        self.workflow_tool.doActionFor(self.obj, 'publish')

        #Now the poll is opened, we cannot retract, nor submit

        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'retract')

        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'submit')

        # We can however send it back only as a site administrator or manager
        self.workflow_tool.doActionFor(self.obj, 'send_back')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'private')

        # Finally, let's open it again, so we can close it
        self.workflow_tool.doActionFor(self.obj, 'publish')
        self.workflow_tool.doActionFor(self.obj, 'close')
        review_state = self.workflow_tool.getInfoFor(self.obj, 'review_state')
        self.assertEqual(review_state, 'closed')

        #Finally, we cannot do anything else from a closed poll
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'retract')

        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'submit')

        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'publish')

    def test_workflow_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # guard-permission: Review portal content
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'publish')
        self.workflow_tool.doActionFor(self.obj, 'submit')
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'publish')

        # Reviewer can retract and publish
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.workflow_tool.doActionFor(self.obj, 'retract')
        self.workflow_tool.doActionFor(self.obj, 'publish')

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # Now, nobody, except manager, can close
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'close')

        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'close')

        # Now, only Site Administrator or Manager can send it back
        setRoles(self.portal, TEST_USER_ID, ['Owner',
                                             'Member',
                                             'Editor',
                                             'Reviewer'])
        self.assertRaises(WorkflowException,
                          self.workflow_tool.doActionFor,
                          self.obj, 'send_back')

        # Manager is already tested in previous test
        setRoles(self.portal, TEST_USER_ID, ['Site Administrator'])
        self.workflow_tool.doActionFor(self.obj, 'send_back')
                          
        # Finally, let's get Manager role, and publish and close
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.workflow_tool.doActionFor(self.obj, 'publish')
        self.workflow_tool.doActionFor(self.obj, 'close')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
