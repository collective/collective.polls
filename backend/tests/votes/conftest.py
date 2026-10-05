"""Fixtures for the vote storage tests."""

from . import OPTIONS
from . import PORTAL_TYPE
from copy import deepcopy
from plone import api
from plone.dexterity.content import DexterityContent

import pytest


@pytest.fixture
def poll(portal) -> DexterityContent:
    """An open poll at the site root, open to anonymous votes."""
    with api.env.adopt_roles(["Manager"]):
        poll = api.content.create(
            portal, PORTAL_TYPE, "poll", options=deepcopy(OPTIONS)
        )
        api.content.transition(obj=poll, transition="open")
    return poll
