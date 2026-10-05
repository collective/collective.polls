"""``normalize_options``: pure function, no Plone needed."""

from collective.polls.options import DuplicateOptionId
from collective.polls.options import normalize_options
from collective.polls.options import OPTIONS_SCHEMA

import json
import jsonschema
import pytest


@pytest.mark.parametrize(
    "options,expected",
    [
        (None, []),
        ([], []),
        (
            [{"description": "Yes"}, {"description": "No"}],
            [
                {"option_id": 0, "description": "Yes"},
                {"option_id": 1, "description": "No"},
            ],
        ),
        (
            ["Yes", "No"],
            [
                {"option_id": 0, "description": "Yes"},
                {"option_id": 1, "description": "No"},
            ],
        ),
        (
            [
                {"option_id": 4, "description": "Kept"},
                {"description": "New"},
                {"option_id": 1, "description": "Also kept"},
                "Newer",
            ],
            [
                {"option_id": 4, "description": "Kept"},
                {"option_id": 5, "description": "New"},
                {"option_id": 1, "description": "Also kept"},
                {"option_id": 6, "description": "Newer"},
            ],
        ),
    ],
)
def test_normalize(options, expected):
    assert normalize_options(options) == expected


def test_ids_are_kept_when_reordered():
    """Reordering never renumbers: votes are counted by id."""
    options = [
        {"option_id": 2, "description": "C"},
        {"option_id": 0, "description": "A"},
        {"option_id": 1, "description": "B"},
    ]
    assert normalize_options(options) == options


def test_extra_keys_are_dropped():
    options = [{"option_id": 0, "description": "A", "votes": 3}]
    assert normalize_options(options) == [{"option_id": 0, "description": "A"}]


def test_idempotent():
    once = normalize_options([
        "A",
        {"description": "B"},
        {"option_id": 9, "description": "C"},
    ])
    assert normalize_options(once) == once


def test_input_not_mutated():
    options = [{"description": "A"}]
    normalize_options(options)
    assert options == [{"description": "A"}]


def test_duplicate_ids():
    with pytest.raises(DuplicateOptionId):
        normalize_options([
            {"option_id": 1, "description": "A"},
            {"option_id": 1, "description": "B"},
        ])


def test_duplicate_is_value_error():
    assert issubclass(DuplicateOptionId, ValueError)


class TestSchema:
    schema = json.loads(OPTIONS_SCHEMA)

    @pytest.mark.parametrize(
        "value",
        [
            [],
            [{"description": "A"}, {"description": "B"}],
            [{"option_id": 0, "description": "A"}],
        ],
    )
    def test_valid(self, value):
        jsonschema.validate(value, self.schema)

    @pytest.mark.parametrize(
        "value",
        [
            {"description": "A"},
            ["A"],
            [{"option_id": 0}],
            [{"description": ""}],
            [{"option_id": -1, "description": "A"}],
            [{"option_id": "0", "description": "A"}],
            [{"description": "A", "extra": 1}],
        ],
    )
    def test_invalid(self, value):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(value, self.schema)
