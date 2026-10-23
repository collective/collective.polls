"""Turn the ``show_results`` Bool of every poll into a choice."""

from collective.polls import logger
from collective.polls.upgrades.v3000.votes import all_polls
from collective.polls.vocabularies.show_results import show_results_choice
from Products.GenericSetup.tool import SetupTool


def convert_show_results(setup_tool: SetupTool) -> None:
    """Store a choice in ``show_results`` wherever a poll still holds a Bool.

    ``True`` showed the results after voting and becomes ``after_vote``;
    ``False`` becomes ``never``. A poll already holding a choice is left
    alone, so running this twice changes nothing.

    :param setup_tool: The ``portal_setup`` tool.
    """
    converted = 0
    for poll in all_polls():
        value = getattr(poll, "show_results", None)
        if isinstance(value, str):
            continue
        poll.show_results = show_results_choice(value)
        converted += 1
    logger.info("Show results: %d polls converted to a choice", converted)
