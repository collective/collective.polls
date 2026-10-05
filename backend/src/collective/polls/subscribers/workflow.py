"""Reactions to workflow transitions on a poll.

Opening a poll is what lets anonymous visitors vote, and sending it back
to private is what clears its votes. Both happen here rather than in the
workflow definition because the definition can only grant a permission to
a fixed set of roles, while the anonymous grant depends on the poll's own
setting and on its parent folder.
"""

from Acquisition import aq_parent
from collective.polls.config import PERMISSION_VOTE
from collective.polls.content.poll import Poll
from collective.polls.interfaces import IPollVotes
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.interfaces import ISiteRoot


#: Roles holding the vote permission on an open poll that anonymous
#: visitors may vote in: the workflow's roles, plus Anonymous.
ALL_ROLES = [
    "Anonymous",
    "Contributor",
    "Editor",
    "Manager",
    "Member",
    "Reader",
    "Reviewer",
    "Site Administrator",
]


def grant_anonymous_vote(poll: Poll) -> bool:
    """Let anonymous visitors vote in a poll, when the poll allows it.

    The grant only happens when anonymous visitors can see the poll: its
    parent is the site root, or Anonymous holds ``View`` on the parent.

    :param poll: The poll.
    :returns: ``True`` when the permission was granted.
    """
    if not poll.allow_anonymous:
        return False
    parent = aq_parent(poll)
    parent_view_roles = [
        role["name"] for role in parent.rolesOfPermission("View") if role["selected"]
    ]
    if not (ISiteRoot.providedBy(parent) or "Anonymous" in parent_view_roles):
        return False
    poll.manage_permission(PERMISSION_VOTE, ALL_ROLES, acquire=0)
    return True


def fix_permissions(poll: Poll, event: IActionSucceededEvent) -> None:
    """Let anonymous visitors vote when a poll is opened.

    :param poll: The poll that transitioned.
    :param event: The workflow event.
    """
    if event.action == "open":
        grant_anonymous_vote(poll)


def remove_votes(poll: Poll, event: IActionSucceededEvent) -> None:
    """Remove every vote when a poll is rejected back to private.

    :param poll: The poll that transitioned.
    :param event: The workflow event.
    """
    if event.action == "reject":
        IPollVotes(poll).clear()
