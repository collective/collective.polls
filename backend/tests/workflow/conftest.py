"""Fixtures for the workflow tests."""

from . import PORTAL_TYPE
from collections.abc import Callable
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.content import DexterityContent

import pytest


@pytest.fixture
def wt(portal):
    """The workflow tool."""
    return api.portal.get_tool("portal_workflow")


@pytest.fixture
def folder(portal) -> DexterityContent:
    """A published, folderish Document."""
    with api.env.adopt_roles(["Manager"]):
        folder = api.content.create(portal, "Document", "folder")
        api.content.transition(obj=folder, transition="publish")
    return folder


@pytest.fixture
def poll(folder) -> DexterityContent:
    """A poll created by the test user, as the legacy tests did."""
    folder.invokeFactory(PORTAL_TYPE, "obj")
    return folder["obj"]


@pytest.fixture
def transition_as_manager(portal, wt) -> Callable[[DexterityContent, str], None]:
    """Return a helper running a transition as a Manager, then logging out."""

    def func(obj: DexterityContent, transition: str) -> None:
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        wt.doActionFor(obj, transition)
        logout()

    return func


@pytest.fixture
def check_permission(portal) -> Callable[[str, DexterityContent], bool]:
    """Return a helper checking a permission for the current user."""
    mt = api.portal.get_tool("portal_membership")

    def func(permission: str, obj: DexterityContent) -> bool:
        return bool(mt.checkPermission(permission, obj))

    return func
