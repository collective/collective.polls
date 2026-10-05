from . import PROFILE
from . import PROFILE_VERSION
from collective.polls import PACKAGE_NAME

import pytest


class TestSetupInstall:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        self.portal = portal

    def test_addon_installed(self, installer):
        """Test if collective.polls is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from collective.polls.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(PROFILE) == PROFILE_VERSION

    @pytest.mark.parametrize(
        "profile",
        [
            "plone.restapi:default",
            "plone.volto:default",
        ],
    )
    def test_dependency_installed(self, setup_tool, profile: str):
        """Profiles the default profile depends on are installed."""
        assert setup_tool.getLastVersionForProfile(profile) != "unknown"
