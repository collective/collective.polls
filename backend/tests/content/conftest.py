"""Fixtures for the content tests."""

from . import OPTIONS
from . import PORTAL_TYPE
from collections.abc import Callable
from copy import deepcopy
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.content import DexterityContent
from ZPublisher.HTTPRequest import HTTPRequest

import pytest


@pytest.fixture
def folder(portal) -> DexterityContent:
    """A published, folderish Document holding the polls."""
    with api.env.adopt_roles(["Manager"]):
        folder = api.content.create(portal, "Document", "folder")
        api.content.transition(obj=folder, transition="publish")
    return folder


@pytest.fixture
def polls(folder) -> dict[str, DexterityContent]:
    """Three polls with three options each, as the legacy tests built them.

    ``p1`` stays private; ``p2`` is open and closed to anonymous votes;
    ``p3`` is open to anonymous votes.
    """
    wt = api.portal.get_tool("portal_workflow")
    with api.env.adopt_roles(["Manager"]):
        for poll_id in ("p1", "p2", "p3"):
            folder.invokeFactory(PORTAL_TYPE, poll_id)
            folder[poll_id].options = deepcopy(OPTIONS)
        folder["p2"].allow_anonymous = False
        wt.doActionFor(folder["p2"], "open")
        wt.doActionFor(folder["p3"], "open")
    return {poll_id: folder[poll_id] for poll_id in ("p1", "p2", "p3")}


@pytest.fixture
def set_request_cookies() -> Callable[[HTTPRequest], None]:
    """Return a helper copying the response cookies into the request.

    That is what the browser does on its next request.
    """

    def func(request: HTTPRequest) -> None:
        for key, cookie in request.response.cookies.items():
            request.cookies[key] = cookie["value"]

    return func


@pytest.fixture
def as_manager(portal) -> Callable[[DexterityContent, str], None]:
    """Return a helper running a transition as a Manager, then logging out.

    Mirrors the legacy ``open_poll``/``reject_poll`` helpers, which left the
    test user logged out afterwards.
    """
    from plone.app.testing import logout

    def func(obj: DexterityContent, transition: str) -> None:
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        api.portal.get_tool("portal_workflow").doActionFor(obj, transition)
        setRoles(portal, TEST_USER_ID, ["Member"])
        logout()

    return func
