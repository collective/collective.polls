"""The example payloads are valid, and each is what the service really answers.

The frontend tests and stories use copies of these files, so this is what
keeps the two halves from drifting apart.
"""

from . import EXAMPLES
from . import SCHEMA
from . import THREE_OPTIONS
from copy import deepcopy

import json
import jsonschema
import pytest


#: Fields that differ per site and per poll.
VOLATILE = ("@id", "uid")

#: Three votes: two for "Yes", one for "No".
VOTERS = {"someone": 0, "someone-else": 0, "voter": 1}

#: example -> (caller, poll arguments)
SCENARIOS = {
    "open": ("member", {"voters": VOTERS}),
    "open-voted": ("voter", {"voters": VOTERS}),
    "open-voted-hidden-results": (
        "voter",
        {"voters": VOTERS, "show_results": False},
    ),
    "open-anonymous": ("anonymous", {"voters": VOTERS}),
    # Only editors see a poll in an unpublished folder.
    "open-anonymous-blocked": ("manager", {"container": "hidden"}),
    "no-votes": ("anonymous", {}),
    "closed": ("anonymous", {"state": "closed", "voters": VOTERS}),
    "private": ("manager", {"state": "private"}),
    # Three voters, five votes: percentages are shares of voters.
    "open-multiple": (
        "voter",
        {
            "options": THREE_OPTIONS,
            "max_choices": 2,
            "legend": "Pick your favourite colours",
            "shuffle_options": True,
            "voters": {"someone": [0, 2], "someone-else": [0], "voter": [1, 2]},
        },
    ),
}


def load(name: str) -> dict:
    return json.loads((EXAMPLES / f"{name}.json").read_text())


def test_every_example_has_a_scenario():
    assert sorted(path.stem for path in EXAMPLES.glob("*.json")) == sorted(SCENARIOS)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_valid(name):
    jsonschema.validate(load(name), SCHEMA)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_real(name, make_poll, session_for):
    username, kwargs = SCENARIOS[name]
    container = kwargs.get("container", "polls")
    make_poll(**deepcopy(kwargs))
    response = session_for(username).get(f"{container}/poll/@poll")
    assert response.status_code == 200, response.text
    real = {k: v for k, v in response.json().items() if k not in VOLATILE}
    example = {k: v for k, v in load(name).items() if k not in VOLATILE}
    assert real == example


@pytest.mark.parametrize(
    "change",
    [
        {"state": "rejected"},
        {"results": [{"option_id": 0, "description": "Yes", "votes": 1}]},
        {"total_votes": None},
        {"has_voted": "no"},
        {"extra": 1},
        {"max_choices": 0},
        {"legend": ""},
        {"shuffle_options": None},
    ],
    ids=[
        "state",
        "result-keys",
        "total-without-results",
        "has-voted",
        "extra",
        "max-choices",
        "empty-legend",
        "shuffle-null",
    ],
)
def test_schema_rejects(change):
    """Control: the schema can fail."""
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**load("closed"), **change}, SCHEMA)
