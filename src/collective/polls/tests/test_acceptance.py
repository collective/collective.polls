# -*- coding: utf-8 -*-

from collective.polls.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_polls.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite
