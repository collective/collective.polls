"""The 2.x tally, copied verbatim, to check migrated polls against.

``_getVotes`` and ``getResults`` are the method bodies of the 2.x
``Poll`` class (``content/poll.py`` at commit 90293e5), with ``self``
replaced by the two things they read: the options and the annotations.
"""

from typing import Any


VOTE_ANNO_KEY = "option.%02d"


def _get_votes(options: list[dict[str, Any]], annotations: Any) -> dict[str, Any]:
    """Return votes in a dict format."""
    votes: dict[str, Any] = {"options": [], "total": 0}
    for option in options:
        index = option.get("option_id")
        description = option.get("description")
        option_votes = annotations.get(VOTE_ANNO_KEY % index, 0)
        votes["options"].append({
            "description": description,
            "votes": option_votes,
            "percentage": 0.0,
        })
        votes["total"] = votes["total"] + option_votes
    for option in votes["options"]:
        if option["votes"]:
            option["percentage"] = option["votes"] / votes["total"]
    return votes


def get_results(
    options: list[dict[str, Any]], annotations: Any
) -> list[tuple[str, int, float]]:
    """Return results so far."""
    votes = _get_votes(options, annotations)
    # Bars show wrong when there are no vote
    if votes["total"] == 0:
        return []
    all_results = []
    for item in votes["options"]:
        all_results.append((item["description"], item["votes"], item["percentage"]))
    return all_results


def total_votes(options: list[dict[str, Any]], annotations: Any) -> int:
    """Return the number of votes so far."""
    votes = _get_votes(options, annotations)
    return votes["total"]
