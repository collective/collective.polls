"""Give anonymous visitors their vote back on open polls."""

from collective.polls import logger
from collective.polls.subscribers.workflow import grant_anonymous_vote
from collective.polls.upgrades.v3000.votes import all_polls
from plone import api
from Products.GenericSetup.tool import SetupTool


def restore_anonymous_vote(setup_tool: SetupTool) -> None:
    """Grant the vote to anonymous visitors on every open poll that allows it.

    2.x reinstalls could run ``updateRoleMappings``, which resets every
    poll's permissions to the workflow's and drops the anonymous grant made
    when the poll was opened. The grant follows the same rules as opening a
    poll does, so running this twice changes nothing.

    :param setup_tool: The ``portal_setup`` tool.
    """
    granted = 0
    for poll in all_polls():
        if api.content.get_state(poll) == "open" and grant_anonymous_vote(poll):
            granted += 1
    logger.info("Permissions: anonymous vote granted on %d open polls", granted)
