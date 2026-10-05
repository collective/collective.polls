"""Fixtures for the service tests.

Content is created in the functional portal and committed, so the requests
made through ``request_factory`` see it.
"""

from . import OPTIONS
from . import PASSWORD
from . import PORTAL_TYPE
from . import SCHEMA
from collections.abc import Callable
from collective.polls.content.poll import Poll
from collective.polls.interfaces import IPollVotes
from copy import deepcopy
from plone import api
from plone.app.testing import setRoles
from plone.dexterity.content import DexterityContent
from Products.CMFPlone.Portal import PloneSite
from pytest_plone.fixtures.requests import RelativeSession
from typing import Any

import jsonschema
import pytest
import transaction


#: Members created for every test: id -> roles.
MEMBERS = {
    "member": ["Member"],
    "voter": ["Member"],
    "reviewer": ["Member", "Reviewer"],
}


@pytest.fixture
def portal(functional_portal) -> PloneSite:
    """The functional portal, with the members and a published folder."""
    with api.env.adopt_roles(["Manager"]):
        for username, roles in MEMBERS.items():
            api.user.create(
                email=f"{username}@example.org",
                username=username,
                password=PASSWORD,
            )
            setRoles(functional_portal, username, roles)
        folder = api.content.create(functional_portal, "Document", "polls")
        api.content.transition(obj=folder, transition="publish")
        api.content.create(functional_portal, "Document", "hidden")
    transaction.commit()
    return functional_portal


@pytest.fixture
def make_poll(portal) -> Callable[..., Poll]:
    """Return a helper creating a poll, committed.

    Keyword arguments: ``state`` (reached through the workflow), ``voters``
    (member id -> option id, recorded directly), ``container`` (the id of a
    folder in the portal, ``polls`` by default), and any schema field.
    """

    def func(
        poll_id: str = "poll",
        state: str = "open",
        voters: dict[str, int] | None = None,
        container: str = "polls",
        **fields: Any,
    ) -> Poll:
        fields.setdefault("options", deepcopy(OPTIONS))
        with api.env.adopt_roles(["Manager"]):
            poll = api.content.create(
                portal[container], PORTAL_TYPE, poll_id, title=poll_id, **fields
            )
            if state in ("open", "closed"):
                api.content.transition(obj=poll, transition="open")
            if state == "closed":
                api.content.transition(obj=poll, transition="close")
            if state == "pending":
                api.content.transition(obj=poll, transition="submit")
        votes = IPollVotes(poll)
        for voter_id, option_id in (voters or {}).items():
            votes.register(option_id, voter_id)
        transaction.commit()
        return poll

    return func


@pytest.fixture
def session_for(request_factory) -> Callable[[str], RelativeSession]:
    """Return a helper opening a REST session as a member, or anonymous.

    ``"anonymous"`` and ``"manager"`` are the two built-in identities; any
    other name is a member from ``MEMBERS``.
    """

    def func(username: str) -> RelativeSession:
        if username == "anonymous":
            return request_factory(role="Anonymous")
        if username == "manager":
            return request_factory(role="Manager")
        return request_factory(basic_auth=(username, PASSWORD))

    return func


@pytest.fixture
def validate() -> Callable[[dict], dict]:
    """Return a helper validating a ``@poll`` payload against the schema."""

    def func(payload: dict) -> dict:
        jsonschema.validate(payload, SCHEMA)
        return payload

    return func


@pytest.fixture
def reload(portal) -> Callable[[DexterityContent | str], DexterityContent]:
    """Return a helper re-reading an object after other requests committed.

    It takes the object, or its path relative to the portal.
    """

    def func(obj: DexterityContent | str) -> DexterityContent:
        transaction.begin()
        if isinstance(obj, str):
            return portal.unrestrictedTraverse(obj)
        return portal.unrestrictedTraverse("/".join(obj.getPhysicalPath()))

    return func
