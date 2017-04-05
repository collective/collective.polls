# -*- coding: utf-8 -*-
"""Setup testing infrastructure.

For Plone 5 we need to install plone.app.contenttypes.

Tile for collective.cover is only tested in Plone 4.3.
"""
from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE
    DEXTERITY_ONLY = False
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE
    DEXTERITY_ONLY = True

try:
    pkg_resources.get_distribution('collective.cover')
except pkg_resources.DistributionNotFound:
    HAS_COVER = False
else:
    HAS_COVER = True

IS_PLONE_42 = api.env.plone_version().startswith('4.2')


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        if HAS_COVER:
            import collective.cover
            self.loadZCML(package=collective.cover)

        import collective.polls
        self.loadZCML(package=collective.polls)

    def setUpPloneSite(self, portal):
        if HAS_COVER:
            self.applyProfile(portal, 'collective.cover:default')
            self.applyProfile(portal, 'collective.polls:testfixture')

        self.applyProfile(portal, 'collective.polls:default')
        wf = getattr(portal, 'portal_workflow')
        types = ('Folder', )
        wf.setChainForPortalTypes(types, 'simple_publication_workflow')

FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name='collective.polls:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE), name='collective.polls:Functional')

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='collective.polls:Robot',
)
