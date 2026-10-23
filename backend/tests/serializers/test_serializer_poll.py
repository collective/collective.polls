"""Who gets the results of a poll, asked of the rule directly."""

from collective.polls.config import PORTAL_TYPE
from collective.polls.serializers.poll import results_visible
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

import pytest


class TestResultsVisible:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        with api.env.adopt_roles(["Manager"]):
            self.poll = api.content.create(
                portal,
                PORTAL_TYPE,
                "poll",
                options=[{"description": "A"}, {"description": "B"}],
            )
        setRoles(portal, TEST_USER_ID, ["Member"])
        login(portal, TEST_USER_NAME)

    @pytest.mark.parametrize("show_results", ["never", "after_vote", "always"])
    @pytest.mark.parametrize("has_voted", [None, False, True])
    def test_not_open(self, show_results, has_voted):
        """Before opening, nobody but reviewers gets results."""
        self.poll.show_results = show_results
        assert results_visible(self.poll, has_voted) is False

    @pytest.mark.parametrize(
        "show_results,has_voted,expected",
        [
            ("never", True, False),
            ("after_vote", None, True),
            ("after_vote", False, False),
            ("after_vote", True, True),
            ("always", False, True),
        ],
    )
    def test_open(self, show_results, has_voted, expected):
        with api.env.adopt_roles(["Manager"]):
            api.content.transition(obj=self.poll, transition="open")
        self.poll.show_results = show_results
        assert results_visible(self.poll, has_voted) is expected
