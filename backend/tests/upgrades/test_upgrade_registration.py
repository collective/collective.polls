"""Every 2.x site is offered the upgrades to 3000 and 3001, 3000 sites only 3001."""

from . import DESTINATION
from . import LATEST
from . import PROFILE
from . import SOURCE
from collective.polls.interfaces import IBrowserLayer
from plone.browserlayer.utils import registered_layers
from plone.browserlayer.utils import unregister_layer

import pytest


#: Every profile version a released 2.x ever had, and the dev one.
LEGACY_VERSIONS = ["1", "2", "3", "4", "5", "6", "7"]


@pytest.mark.parametrize("version", LEGACY_VERSIONS)
def test_offered(setup_tool, upgrade_steps, version):
    setup_tool.setLastVersionForProfile(PROFILE, version)
    steps = upgrade_steps()
    assert {s["sdest"] for s in steps} == {DESTINATION, LATEST}
    assert [s["title"] for s in steps] == [
        "Re-apply the browser layer, type, workflow and permissions",
        "Move votes to the 3.0 storage",
        "Remove vote portlets",
        "Let anonymous visitors vote in open polls again",
        "Remove registrations of 2.x tiles and resources",
        "Check that plone.volto is installed",
        "Turn show_results into a choice",
    ]


def test_3001_offered_to_3000(setup_tool, upgrade_steps):
    setup_tool.setLastVersionForProfile(PROFILE, DESTINATION)
    steps = upgrade_steps()
    assert {s["sdest"] for s in steps} == {LATEST}
    assert [s["title"] for s in steps] == ["Turn show_results into a choice"]


def test_not_offered_when_current(setup_tool, upgrade_steps):
    assert setup_tool.getLastVersionForProfile(PROFILE) == (LATEST,)
    assert upgrade_steps() == []


def test_upgrade_from_2x(portal, setup_tool):
    """A 2.x site without the browser layer ends current, with the layer."""
    unregister_layer("collective.polls")
    assert IBrowserLayer not in registered_layers()
    setup_tool.setLastVersionForProfile(PROFILE, SOURCE)
    setup_tool.upgradeProfile(PROFILE)
    assert setup_tool.getLastVersionForProfile(PROFILE) == (LATEST,)
    assert IBrowserLayer in registered_layers()
