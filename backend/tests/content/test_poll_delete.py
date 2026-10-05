"""A Manager can delete a poll in every workflow state (issue #135)."""

from plone import api

import pytest


@pytest.mark.parametrize(
    "transitions,state",
    [
        ([], "private"),
        (["submit"], "pending"),
        (["open"], "open"),
        (["open", "close"], "closed"),
    ],
)
def test_manager_deletes_poll(polls, transitions: list[str], state: str):
    poll = polls["p1"]
    folder = poll.__parent__
    with api.env.adopt_roles(["Manager"]):
        for transition in transitions:
            api.content.transition(obj=poll, transition=transition)
        assert api.content.get_state(obj=poll) == state
        api.content.delete(obj=poll)
    assert "p1" not in folder
