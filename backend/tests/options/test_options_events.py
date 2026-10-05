"""Options get ids when a poll is added or modified through ``plone.api``."""

from . import PORTAL_TYPE
from collective.polls.content.poll import DuplicateOptions
from collective.polls.content.poll import IPoll
from collective.polls.subscribers import options as handlers
from plone import api
from types import SimpleNamespace
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import pytest
import transaction


class TestOptionsEvents:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        self.portal = portal
        with api.env.adopt_roles(["Manager"]):
            self.poll = api.content.create(
                portal,
                PORTAL_TYPE,
                "poll",
                options=[{"description": "Yes"}, "No"],
            )

    def test_ids_assigned_on_add(self):
        assert self.poll.options == [
            {"option_id": 0, "description": "Yes"},
            {"option_id": 1, "description": "No"},
        ]

    def test_ids_assigned_on_modify(self):
        self.poll.options = [*self.poll.options, {"description": "Maybe"}]
        notify(ObjectModifiedEvent(self.poll))
        assert self.poll.options[-1] == {"option_id": 2, "description": "Maybe"}

    def test_ids_kept_on_reorder(self):
        self.poll.options = list(reversed(self.poll.options))
        notify(ObjectModifiedEvent(self.poll))
        assert [o["option_id"] for o in self.poll.options] == [1, 0]

    def test_no_write_when_unchanged(self):
        """A vote fires the same event; the handler must not rewrite the poll.

        Called directly: other ``ObjectModifiedEvent`` handlers do write the
        poll (its modification date), which is not this handler's doing.
        """
        transaction.savepoint()
        assert not self.poll._p_changed
        handlers.normalize_poll_options(self.poll, ObjectModifiedEvent(self.poll))
        assert not self.poll._p_changed


def test_invariant_rejects_duplicate_ids():
    data = SimpleNamespace(
        options=[
            {"option_id": 1, "description": "A"},
            {"option_id": 1, "description": "B"},
        ]
    )
    with pytest.raises(DuplicateOptions):
        IPoll.validateInvariants(data)
