"""Fixtures for the plone.exportimport tests."""

from . import OPTIONS
from . import PORTAL_TYPE
from . import VOTERS
from collections.abc import Callable
from collections.abc import Generator
from collective.polls.content.poll import Poll
from collective.polls.interfaces import IPollVotes
from copy import deepcopy
from plone import api
from plone.exportimport.importers.base import BaseImporter
from plone.exportimport.interfaces import IExportImportRequestMarker
from plone.exportimport.utils import request_provides
from ZPublisher.HTTPRequest import HTTPRequest

import pytest


@pytest.fixture
def make_poll(portal) -> Callable[..., Poll]:
    """Return a helper creating a poll at the site root, with votes.

    Keyword arguments: ``state`` (reached through the workflow) and
    ``voters`` (voter id -> option id, :data:`VOTERS` by default).
    """

    def func(
        poll_id: str = "poll",
        state: str = "closed",
        voters: dict[str, int] | None = None,
    ) -> Poll:
        with api.env.adopt_roles(["Manager"]):
            poll = api.content.create(
                portal, PORTAL_TYPE, poll_id, title=poll_id, options=deepcopy(OPTIONS)
            )
            if state in ("open", "closed"):
                api.content.transition(obj=poll, transition="open")
            if state == "closed":
                api.content.transition(obj=poll, transition="close")
        votes = IPollVotes(poll)
        for voter_id, option_id in (VOTERS if voters is None else voters).items():
            votes.register(option_id, voter_id)
        return poll

    return func


@pytest.fixture
def exportimport_request(http_request) -> Generator[HTTPRequest]:
    """Yield the request as plone.exportimport marks it while it runs."""
    with request_provides(http_request, IExportImportRequestMarker):
        yield http_request


@pytest.fixture
def no_commits(monkeypatch) -> None:
    """Keep the importers from committing, which the test layer forbids."""
    monkeypatch.setattr(BaseImporter, "intermediate_commits", False)
