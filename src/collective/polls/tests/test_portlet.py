# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.uuid.interfaces import IUUID

from Products.GenericSetup.utils import _getDottedName

from collective.polls.portlet import voteportlet

from collective.polls.testing import INTEGRATION_TESTING


class BasePortlet(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _set_request_cookies(self, request):
        ''' For each cookie in response, we set a cookie in request '''
        response_cookies = request.response.cookies
        for key, cookie in response_cookies.items():
            request.cookies[key] = cookie['value']

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = self.portal.portal_workflow
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.wt.doActionFor(self.folder, 'publish')
        self.setUpPolls()

    def setUpPolls(self):
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
        p3 = self.folder['p3']
        p3.options = options
        p3.allow_anonymous = True
        # Open p2 and p3
        wt.doActionFor(self.folder['p2'], 'open')
        wt.doActionFor(self.folder['p3'], 'open')
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3


class PortletRegistrationTest(BasePortlet):

    def test_portlet_registered(self):
        portlet = queryUtility(IPortletType,
                               name='collective.polls.VotePortlet')
        self.assertEqual(portlet.addview, 'collective.polls.VotePortlet')

    def test_registered_interfaces(self):
        portlet = queryUtility(IPortletType,
                               name='collective.polls.VotePortlet')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(['plone.app.portlets.interfaces.IColumn',
                           'plone.app.portlets.interfaces.IDashboard'],
                          registered_interfaces)

    def test_interfaces(self):
        portlet = voteportlet.Assignment(header='Polls',
                                         poll='latest')
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portal = self.portal
        traversal = '++contextportlets++plone.leftcolumn'
        portlet = queryUtility(IPortletType,
                               name='collective.polls.VotePortlet')
        mapping = portal.restrictedTraverse(traversal)
        for m in mapping.keys():
            # Remove all assignments
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'header': 'Polls', 'poll': 'latest'})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                   voteportlet.Assignment))

    def test_invoke_editview(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = voteportlet.Assignment(header='Polls',
                                         poll='latest')
        editview = getMultiAdapter((mapping['foo'], request),
                                    name='edit')
        self.assertTrue(isinstance(editview, voteportlet.EditForm))

    def test_vocab_possible_polls(self):
        ''' test vocabulary source for possible polls '''
        portal = self.portal
        vocab = voteportlet.PossiblePolls(portal)
        # We should list here 2 open polls + latest as options
        self.assertEqual(len(vocab), 3)

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager,
                             name='plone.leftcolumn',
                             context=self.portal)
        assignment = voteportlet.Assignment(header='Polls',
                                             poll='latest')

        renderer = getMultiAdapter((context, request, view, manager, assignment),
                                    IPortletRenderer)
        self.assertTrue(isinstance(renderer, voteportlet.Renderer))

    def test_renderer_anonymous(self):
        NotImplemented


class PortletRendererTest(BasePortlet):

    def renderer(self, context=None, request=None, view=None,
                 manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
                                        name='plone.leftcolumn',
                                        context=self.portal)

        return getMultiAdapter((context, request, view, manager, assignment),
                                IPortletRenderer)

    def test_available(self):
        # Use a opened poll
        poll_uid = IUUID(self.p3)
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll=poll_uid))
        self.assertEqual(True, r.available)

    def test_available_anonymous(self):
        # Use a opened poll
        poll_uid = IUUID(self.p3)
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll=poll_uid))
        logout()
        self.assertEqual(True, r.available)

    def test_not_available(self):
        # Use a non-opened poll
        poll_uid = IUUID(self.p1)
        logout()
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll=poll_uid))
        self.assertEqual(False, r.available)

    def test_options(self):
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll='latest'))
        self.assertEqual(3, len(r.poll().options))

    def test_all_polls_closed_dont_show_closed(self):
        wt = self.wt
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        wt.doActionFor(self.p2, 'close')
        wt.doActionFor(self.p3, 'close')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll='latest',
                                                            show_closed=False))
        self.assertEqual(False, r.available)

    def test_all_polls_closed_do_show_closed(self):
        wt = self.wt
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        wt.doActionFor(self.p2, 'close')
        wt.doActionFor(self.p3, 'close')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        r = self.renderer(assignment=voteportlet.Assignment(header='Polls',
                                                            poll='latest',
                                                            show_closed=True))
        self.assertEqual(True, r.available)
        self.assertEqual(3, len(r.poll().options))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
