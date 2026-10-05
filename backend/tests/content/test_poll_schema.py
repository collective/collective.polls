from . import PORTAL_TYPE
from collective.polls.content.poll import InsufficientOptions
from collective.polls.content.poll import InsuficientOptions
from collective.polls.content.poll import IPoll
from plone import api
from types import SimpleNamespace

import pytest


class TestPollSchema:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        self.portal = portal
        with api.env.adopt_roles(["Manager"]):
            self.poll = api.content.create(portal, PORTAL_TYPE, "poll")

    def test_adding(self):
        assert IPoll.providedBy(self.poll)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("allow_anonymous", True),
            ("show_results", True),
            ("results_graph", "bar"),
            ("options", []),
        ],
    )
    def test_default_values(self, field: str, value):
        """A new poll gets the legacy defaults."""
        assert getattr(self.poll, field) == value

    def test_results_graph_vocabulary(self):
        """``results_graph`` uses the named vocabulary."""
        assert IPoll["results_graph"].vocabularyName == "collective.polls.ResultsGraph"

    def test_misspelled_exception_name(self):
        """The legacy name still refers to the same class."""
        assert InsuficientOptions is InsufficientOptions


class TestPollInvariant:
    @pytest.mark.parametrize(
        "options",
        [
            None,
            [],
            [{"option_id": 0, "description": "Foo"}],
        ],
    )
    def test_not_enough_options(self, options):
        """Fewer than two options fail validation."""
        with pytest.raises(InsufficientOptions):
            IPoll.validateInvariants(SimpleNamespace(options=options))

    def test_two_options(self):
        """Two options pass validation."""
        data = SimpleNamespace(
            options=[
                {"option_id": 0, "description": "Foo"},
                {"option_id": 1, "description": "Bar"},
            ]
        )
        assert IPoll.validateInvariants(data) is None
