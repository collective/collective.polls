"""The permission matrix of ``poll_workflow``, state by state.

The poll is closed to anonymous votes, so the open state shows the
workflow's own mapping and not the grant the ``open`` subscriber adds.
"""

from . import mapping_for
from . import PATH_TO
from . import PERMISSION_MAP
from plone import api

import pytest


@pytest.mark.parametrize(
    "state,permission",
    sorted(PERMISSION_MAP),
    ids=[f"{state}-{permission}" for state, permission in sorted(PERMISSION_MAP)],
)
def test_permission_map(poll, state: str, permission: str):
    poll.allow_anonymous = False
    with api.env.adopt_roles(["Manager"]):
        for transition in PATH_TO[state]:
            api.content.transition(obj=poll, transition=transition)
    assert api.content.get_state(obj=poll) == state
    assert mapping_for(poll, permission) == PERMISSION_MAP[(state, permission)]


def test_matrix_complete():
    """Every managed permission is covered in every state."""
    assert len(PERMISSION_MAP) == 16
