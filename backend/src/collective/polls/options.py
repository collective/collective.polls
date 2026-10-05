"""The options of a poll, and how they get stable ids.

An option is stored as ``{"option_id": int, "description": str}``, the
shape the package has always used. Votes are counted per ``option_id``, so
the id of an existing option must never change: an option that arrives with
an id keeps it, and one that arrives without gets the next free id.
"""

from collective.polls.interfaces import PollOptionDict
from typing import Any

import json


#: JSON schema of the ``options`` field. "At least two options" is not here:
#: zope.schema validates the field's default, an empty list, against this
#: schema, so the rule lives in the ``IPoll`` invariant instead.
OPTIONS_SCHEMA = json.dumps({
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "option_id": {"type": "integer", "minimum": 0},
            "description": {"type": "string", "minLength": 1},
        },
        "required": ["description"],
        "additionalProperties": False,
    },
})


class DuplicateOptionId(ValueError):
    """Two options of a poll share an id."""


def normalize_options(options: Any) -> list[PollOptionDict]:
    """Give every option a stable id.

    Options that already have an ``option_id`` keep it. Options without one,
    and bare strings, get ``max(existing ids) + 1``, in order. Calling this
    on its own result returns an equal list.

    :param options: The options as stored or received; ``None`` is empty.
    :returns: A new list of ``{"option_id", "description"}`` dicts.
    :raises DuplicateOptionId: When two options carry the same id.
    """
    entries: list[dict] = [
        {"description": option} if isinstance(option, str) else dict(option)
        for option in options or []
    ]
    seen: set[int] = set()
    for entry in entries:
        option_id = entry.get("option_id")
        if option_id is None:
            continue
        if option_id in seen:
            raise DuplicateOptionId(f"Duplicate option id: {option_id}")
        seen.add(option_id)
    next_id = max(seen) + 1 if seen else 0
    result: list[PollOptionDict] = []
    for entry in entries:
        option_id = entry.get("option_id")
        if option_id is None:
            option_id = next_id
            next_id += 1
        result.append({"option_id": option_id, "description": entry["description"]})
    return result
