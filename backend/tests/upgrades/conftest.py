"""Fixtures for the upgrade tests."""

from . import PROFILE
from collections.abc import Callable
from plone import api
from plone.dexterity.content import DexterityContent
from Products.GenericSetup.tool import SetupTool
from typing import Any

import pytest


@pytest.fixture
def folder(portal) -> DexterityContent:
    """A published, folderish Document holding the polls."""
    with api.env.adopt_roles(["Manager"]):
        folder = api.content.create(portal, "Document", "folder")
        api.content.transition(obj=folder, transition="publish")
    return folder


@pytest.fixture
def upgrade_steps(setup_tool) -> Callable[[], list[dict[str, Any]]]:
    """Return a helper listing the steps offered for the profile, flattened.

    ``listUpgrades`` gives a grouped ``upgradeSteps`` as one list.
    """

    def func() -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for entry in setup_tool.listUpgrades(PROFILE):
            steps.extend(entry if isinstance(entry, list) else [entry])
        return steps

    return func


@pytest.fixture
def run_step(setup_tool: SetupTool) -> Callable[[Callable[[SetupTool], None]], None]:
    """Return a helper running one upgrade handler as Manager."""

    def func(handler: Callable[[SetupTool], None]) -> None:
        with api.env.adopt_roles(["Manager"]):
            handler(setup_tool)

    return func
