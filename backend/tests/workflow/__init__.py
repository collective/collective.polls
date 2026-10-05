"""``poll_workflow``: its graph, its permission matrix, who can move a poll.

The expected values are written out here rather than read from the
definition, so a change to the XML has to be made twice to go unnoticed.
"""

from AccessControl.Permission import Permission
from collective.polls.config import PERMISSION_VOTE
from collective.polls.config import PORTAL_TYPE
from collective.polls.config import WORKFLOW_ID
from typing import Any


ACCESS = "Access contents information"
MODIFY = "Modify portal content"
VIEW = "View"
VOTE = PERMISSION_VOTE

#: Every permission the workflow manages.
MANAGED_PERMISSIONS = (ACCESS, MODIFY, VIEW, VOTE)

INITIAL_STATE = "private"

#: state -> exit transitions
STATES = {
    "private": ("open", "submit"),
    "pending": ("open", "reject", "retract"),
    "open": ("close", "reject"),
    "closed": ("open",),
}

#: transition -> (new state, guard permission)
TRANSITIONS = {
    "close": ("closed", "collective.polls: Close poll"),
    "open": ("open", "Review portal content"),
    "reject": ("private", "Review portal content"),
    "retract": ("private", "Request review"),
    "submit": ("pending", "Request review"),
}

_EDITORS = ("Contributor", "Editor", "Manager", "Owner", "Reader", "Site Administrator")

#: (state, permission) -> (acquire, roles). Roles sorted.
PERMISSION_MAP = {
    ("private", ACCESS): (False, _EDITORS),
    ("private", MODIFY): (False, ("Editor", "Manager", "Owner", "Site Administrator")),
    ("private", VIEW): (False, _EDITORS),
    ("private", VOTE): (False, ()),
    ("pending", ACCESS): (False, tuple(sorted((*_EDITORS, "Reviewer")))),
    ("pending", MODIFY): (False, ("Manager", "Reviewer", "Site Administrator")),
    ("pending", VIEW): (False, tuple(sorted((*_EDITORS, "Reviewer")))),
    ("pending", VOTE): (False, ()),
    ("open", ACCESS): (True, ()),
    ("open", MODIFY): (False, ()),
    ("open", VIEW): (True, ()),
    (
        "open",
        VOTE,
    ): (
        False,
        (
            "Contributor",
            "Editor",
            "Manager",
            "Member",
            "Reader",
            "Reviewer",
            "Site Administrator",
        ),
    ),
    ("closed", ACCESS): (True, ()),
    ("closed", MODIFY): (False, ()),
    ("closed", VIEW): (True, ()),
    ("closed", VOTE): (False, ()),
}

#: Transitions that lead from the initial state to each state.
PATH_TO = {
    "private": (),
    "pending": ("submit",),
    "open": ("open",),
    "closed": ("open", "close"),
}


def mapping_for(obj: Any, permission: str) -> tuple[bool, tuple[str, ...]]:
    """Read how a permission is mapped on one object.

    Reads the attribute ``manage_permission`` writes -- what a workflow's role
    mapping actually sets. Zope stores a list when the mapping acquires and a
    tuple when it does not.

    :param obj: Object to read the mapping from.
    :param permission: Title of the permission.
    :returns: ``(acquire, sorted roles)``.
    """
    roles = Permission(permission, (), obj).getRoles(default=[])
    return isinstance(roles, list), tuple(sorted(roles))


__all__ = ["PORTAL_TYPE", "WORKFLOW_ID"]
