# -*- coding: utf-8 -*-
"""Tests in this module are executed only if collective.cover is installed."""
from collective.polls.testing import HAS_COVER
from collective.polls.testing import INTEGRATION_TESTING

import unittest


if HAS_COVER:
    from collective.cover.tests.base import TestTileMixin
    from collective.polls.tiles.poll import IPollTile
    from collective.polls.tiles.poll import PollTile
else:  # skip tests
    class TestTileMixin:
        pass

    def test_suite():
        return unittest.TestSuite()


class PollTileTestCase(TestTileMixin, unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        super(PollTileTestCase, self).setUp()
        self.tile = PollTile(self.cover, self.request)
        self.tile.__name__ = u'collective.polls'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IPollTile
        self.klass = PollTile
        super(PollTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertListEqual(
            self.tile.accepted_ct(), ['collective.polls.poll'])
