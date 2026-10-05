"""Profiles: what is offered for installation, and that every file parses."""

from collective.polls import PACKAGE_NAME
from collective.polls.setuphandlers import HiddenProfiles
from lxml import etree
from pathlib import Path

import collective.polls
import pytest


PROFILES = Path(collective.polls.__file__).parent / "profiles"

XML_FILES = sorted(PROFILES.rglob("*.xml"))


def _relative(path: Path) -> str:
    return str(path.relative_to(PROFILES))


class TestHiddenProfiles:
    def test_profiles(self):
        """Only the uninstall profile is hidden."""
        assert HiddenProfiles().getNonInstallableProfiles() == [
            f"{PACKAGE_NAME}:uninstall"
        ]

    def test_products(self):
        """The upgrades package is never offered as a product."""
        assert HiddenProfiles().getNonInstallableProducts() == [
            f"{PACKAGE_NAME}.upgrades"
        ]


def test_profiles_folder_found():
    """Guard the glob, so an empty parametrize cannot pass silently."""
    assert len(XML_FILES) > 5


@pytest.mark.parametrize("path", XML_FILES, ids=_relative)
def test_xml_is_well_formed(path: Path):
    """A file GenericSetup cannot parse takes the whole profile with it."""
    assert etree.fromstring(path.read_bytes()) is not None
