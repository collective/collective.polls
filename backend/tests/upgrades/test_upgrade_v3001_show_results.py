"""Upgrade to 3001: the ``show_results`` Bool of every poll becomes a choice."""

from . import PORTAL_TYPE
from collective.polls.upgrades.v3001 import show_results as step
from plone import api

import pytest


class TestConvert:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, folder, run_step) -> None:
        self.folder = folder
        self.run_step = run_step

    def make(self, poll_id: str, stored) -> object:
        """A poll holding ``stored``, as a 3.0.0a1 or 2.x site saved it."""
        with api.env.adopt_roles(["Manager"]):
            poll = api.content.create(
                self.folder,
                PORTAL_TYPE,
                poll_id,
                options=[{"description": "A"}, {"description": "B"}],
            )
        poll.show_results = stored
        return poll

    @pytest.mark.parametrize(
        "stored,expected",
        [
            (True, "after_vote"),
            (False, "never"),
            (None, "after_vote"),
            ("never", "never"),
            ("always", "always"),
        ],
    )
    def test_converted(self, stored, expected):
        poll = self.make("poll", stored)
        self.run_step(step.convert_show_results)
        assert poll.show_results == expected

    def test_missing_attribute(self):
        """A poll storing nothing reads the new default, so it is left alone."""
        poll = self.make("poll", True)
        del poll.show_results
        self.run_step(step.convert_show_results)
        assert "show_results" not in poll.__dict__
        assert poll.show_results == "after_vote"

    def test_twice(self):
        polls = [self.make("p1", True), self.make("p2", False)]
        self.run_step(step.convert_show_results)
        self.run_step(step.convert_show_results)
        assert [p.show_results for p in polls] == ["after_vote", "never"]

    def test_logged(self, caplog):
        self.make("p1", True)
        self.make("p2", "always")
        with caplog.at_level("INFO"):
            self.run_step(step.convert_show_results)
        assert "Show results: 1 polls converted to a choice" in caplog.text
