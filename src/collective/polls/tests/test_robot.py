# -*- coding: utf-8 -*-
from collective.polls.testing import ROBOT_TESTING
from plone import api
from plone.testing import layered

import os
import robotsuite
import unittest

PLONE_VERSION = api.env.plone_version()
IS_PLONE_42 = PLONE_VERSION.startswith('4.2')

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]

# skip RobotFramework tests in Plone 4.2
# FIXME: https://github.com/collective/collective.polls/issues/103
if IS_PLONE_42:
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
