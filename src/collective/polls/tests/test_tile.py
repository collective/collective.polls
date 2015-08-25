# -*- coding: utf-8 -*-
from collective.cover.tiles.base import IPersistentCoverTile
from collective.polls.testing import INTEGRATION_TESTING
from collective.polls.tiles.poll import PollTile
from plone import api
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class PollTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.polls', 'test-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(PollTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, PollTile))

        tile = PollTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertListEqual(
            self.tile.accepted_ct(), ['collective.polls.poll'])


def test_suite():
    """Load tile tests only in Plone < 5.0."""
    # from collective.polls.testing import PLONE_VERSION
    PLONE_VERSION = api.env.plone_version()
    if PLONE_VERSION < '5.0':
        return unittest.defaultTestLoader.loadTestsFromName(__name__)
    else:
        return unittest.TestSuite()
