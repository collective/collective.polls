import unittest

import robotsuite

from plone.testing import layered

from collective.polls.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_polls.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite
