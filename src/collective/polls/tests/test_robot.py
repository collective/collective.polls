# -*- coding: utf-8 -*-
from collective.polls.config import IS_PLONE_5
from collective.polls.testing import IS_PLONE_42
from collective.polls.testing import ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest


dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]

# skip RobotFramework tests in Plone 4.2
# FIXME: https://github.com/collective/collective.polls/issues/103
if IS_PLONE_42:
    tests = []

# skip RobotFramework tests in Plone 5
if IS_PLONE_5:
    tests = []


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite(t, noncritical=['Expected Failure']),
            layer=ROBOT_TESTING)
        for t in tests
    ])
    return suite
