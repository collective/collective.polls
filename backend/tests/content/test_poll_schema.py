from . import PORTAL_TYPE
from collective.polls.content.poll import InsufficientOptions
from collective.polls.content.poll import InsuficientOptions
from collective.polls.content.poll import IPoll
from collective.polls.content.poll import TooManyChoices
from plone import api
from plone.supermodel.interfaces import FIELDSETS_KEY
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
            ("max_choices", 1),
            ("legend", None),
            ("shuffle_options", False),
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


TWO_OPTIONS = [
    {"option_id": 0, "description": "Foo"},
    {"option_id": 1, "description": "Bar"},
]


class TestMaxChoicesInvariant:
    @pytest.mark.parametrize("max_choices", [None, 1, 2])
    def test_within_options(self, max_choices):
        data = SimpleNamespace(options=TWO_OPTIONS, max_choices=max_choices)
        assert IPoll.validateInvariants(data) is None

    def test_more_than_options(self):
        data = SimpleNamespace(options=TWO_OPTIONS, max_choices=3)
        with pytest.raises(TooManyChoices):
            IPoll.validateInvariants(data)

    def test_missing_attribute(self):
        """Polls saved before the field existed validate as single choice."""
        assert IPoll.validateInvariants(SimpleNamespace(options=TWO_OPTIONS)) is None


class TestFieldsets:
    def test_fieldsets(self):
        fieldsets = {
            fs.__name__: fs.fields for fs in IPoll.queryTaggedValue(FIELDSETS_KEY)
        }
        assert fieldsets == {
            "voting": [
                "allow_anonymous",
                "max_choices",
                "legend",
                "options",
                "shuffle_options",
            ],
            "results": ["show_results", "results_graph"],
        }
