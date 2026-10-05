"""Site-wide role mappings of the three permissions.

The vote permission is granted to nobody at the site root: only an open
poll grants it, through its workflow.
"""

from . import ADD_POLL
from . import CLOSE_POLL
from . import VOTE

import pytest


class TestSetupPermissions:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        self.portal = portal

    @pytest.mark.parametrize(
        "permission,roles",
        [
            (ADD_POLL, ["Contributor", "Manager", "Owner", "Site Administrator"]),
            (CLOSE_POLL, ["Manager", "Reviewer", "Site Administrator"]),
            (VOTE, []),
        ],
    )
    def test_roles(self, permission: str, roles: list[str]):
        """Each permission is granted to exactly these roles."""
        granted = [
            role["name"]
            for role in self.portal.rolesOfPermission(permission)
            if role["selected"]
        ]
        assert granted == roles

    @pytest.mark.parametrize(
        "permission,acquire",
        [
            (ADD_POLL, True),
            (CLOSE_POLL, True),
            (VOTE, False),
        ],
    )
    def test_acquire(self, permission: str, acquire: bool):
        """Only the vote permission stops acquisition at the site root."""
        settings = self.portal.permission_settings(permission)[0]
        assert bool(settings["acquire"]) is acquire
