"""The ``initial`` profile imports the example content."""

from plone import api
from plone.exportimport.importers.base import BaseImporter

import pytest


class TestSetupInitial:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, setup_tool, monkeypatch) -> None:
        self.portal = portal
        # The importers commit along the way, which would leak the example
        # content into the layer, and from there into every later test.
        monkeypatch.setattr(BaseImporter, "intermediate_commits", False)
        with api.env.adopt_roles(["Manager"]):
            setup_tool.runAllImportStepsFromProfile("profile-collective.polls:initial")

    @pytest.mark.parametrize(
        "path,portal_type",
        [
            ("images", "Document"),
            ("images/plone-foundation.png", "Image"),
        ],
    )
    def test_example_content(self, path: str, portal_type: str):
        """The example content exists after applying the profile."""
        content = self.portal.unrestrictedTraverse(path)
        assert content.portal_type == portal_type
