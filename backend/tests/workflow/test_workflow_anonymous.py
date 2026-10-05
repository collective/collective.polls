"""What anonymous visitors may see and vote on, state by state.

Ported from the legacy suite: a poll at the site root, in a published
folder, and in a folder anonymous visitors cannot see.
"""

from . import PORTAL_TYPE
from . import VIEW
from . import VOTE
from plone import api
from plone.app.testing import logout

import pytest


#: state -> transitions from private, run one by one
STEPS = (
    ("private", ()),
    ("pending", ("submit",)),
    ("open", ("retract", "open")),
    ("closed", ("close",)),
)


def _walk(obj, transition_as_manager, check_permission, permission: str) -> dict:
    """Move the poll through every state and record the anonymous check."""
    results = {}
    for state, transitions in STEPS:
        for transition in transitions:
            transition_as_manager(obj, transition)
        logout()
        results[state] = check_permission(permission, obj)
    return results


class TestAnonymousPublishedFolder:
    def test_view(self, poll, transition_as_manager, check_permission):
        results = _walk(poll, transition_as_manager, check_permission, VIEW)
        assert results == {
            "private": False,
            "pending": False,
            "open": True,
            "closed": True,
        }

    def test_vote(self, poll, transition_as_manager, check_permission):
        results = _walk(poll, transition_as_manager, check_permission, VOTE)
        assert results == {
            "private": False,
            "pending": False,
            "open": True,
            "closed": False,
        }


class TestAnonymousPrivateFolder:
    @pytest.fixture(autouse=True)
    def _setup(self, folder) -> None:
        # View only to Members in the folder containing our poll
        folder.manage_permission("View", ["Member"], acquire=0)

    def test_view(self, poll, transition_as_manager, check_permission):
        results = _walk(poll, transition_as_manager, check_permission, VIEW)
        assert set(results.values()) == {False}

    def test_vote(self, poll, transition_as_manager, check_permission):
        results = _walk(poll, transition_as_manager, check_permission, VOTE)
        assert set(results.values()) == {False}


class TestAnonymousSiteRoot:
    @pytest.fixture
    def root_poll(self, portal):
        with api.env.adopt_roles(["Manager"]):
            portal.invokeFactory(PORTAL_TYPE, "obj-root")
        return portal["obj-root"]

    def test_vote(self, root_poll, transition_as_manager, check_permission):
        """A poll at the root accepts anonymous votes once open."""
        results = _walk(root_poll, transition_as_manager, check_permission, VOTE)
        assert results == {
            "private": False,
            "pending": False,
            "open": True,
            "closed": False,
        }
