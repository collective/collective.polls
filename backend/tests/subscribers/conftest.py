"""Fixtures for the subscriber tests."""

from . import OPTIONS
from . import PORTAL_TYPE
from collections.abc import Callable
from copy import deepcopy
from plone import api
from plone.dexterity.content import DexterityContent

import pytest


@pytest.fixture
def make_poll(portal) -> Callable[..., DexterityContent]:
    """Return a factory creating a poll, as a Manager.

    :returns: Callable taking the container (``None`` for a folder anonymous
        visitors can see, ``"root"`` for the site root, ``"private"`` for a
        folder they cannot see) and the poll's ``allow_anonymous``.
    """

    def func(
        where: str | None = None, allow_anonymous: bool = True
    ) -> DexterityContent:
        with api.env.adopt_roles(["Manager"]):
            if where == "root":
                container = portal
            else:
                container = api.content.create(portal, "Document", "folder")
                if where != "private":
                    api.content.transition(obj=container, transition="publish")
            poll = api.content.create(
                container,
                PORTAL_TYPE,
                "poll",
                options=deepcopy(OPTIONS),
                allow_anonymous=allow_anonymous,
            )
        return poll

    return func


@pytest.fixture
def transition() -> Callable[[DexterityContent, str], None]:
    """Return a helper running a transition as a Manager."""

    def func(obj: DexterityContent, transition_id: str) -> None:
        with api.env.adopt_roles(["Manager"]):
            api.content.transition(obj=obj, transition=transition_id)

    return func
