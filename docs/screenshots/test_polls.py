"""Capture polls as visitors and editors see them in the example content.

Every script only reads: the add form and the page editor are photographed and
left without saving, and nobody votes.
"""

from .conftest import FRONTEND

#: The example content's polls.
AWAY_TEAM = "/all-polls/away-team"
CHOOSE_A_CAPTAIN = "/all-polls/choose-a-captain"

#: The add form of a poll, inside the example content's folder of polls.
ADD_POLL = "/all-polls/add?type=collective.polls.poll"

#: The add form itself; a bare ``form`` would match the header's search box.
ADD_FORM = "#page-add .ui.raised.segments"


def _open_tab(page, title: str) -> None:
    """Switch the add form to one of its fieldset tabs.

    :param page: The page showing the add form.
    :param title: The tab's title.
    """
    page.locator(".menu .item").filter(has_text=title).first.click()


def test_home_poll_blocks(anonymous_page, shot) -> None:
    """The home page: three Poll blocks in a grid, as a visitor sees them."""
    anonymous_page.goto(FRONTEND)
    anonymous_page.wait_for_selector(".poll-results-pie")
    shot.capture("home-poll-blocks")


def test_poll_multiple_choice(anonymous_page, shot) -> None:
    """A multiple choice poll's form, with its checkboxes."""
    anonymous_page.goto(f"{FRONTEND}{AWAY_TEAM}")
    anonymous_page.wait_for_selector(".poll-form input[type=checkbox]")
    shot.capture("poll-multiple-choice", element=anonymous_page.locator(".poll-view"))


def test_poll_closed_results(anonymous_page, shot) -> None:
    """A closed poll's final results, which every visitor sees."""
    anonymous_page.goto(f"{FRONTEND}{CHOOSE_A_CAPTAIN}")
    anonymous_page.wait_for_selector(".poll-results-pie")
    shot.capture("poll-closed-results", element=anonymous_page.locator(".poll-view"))


def test_poll_add_voting(page_as_admin, shot) -> None:
    """The Voting tab of the add form, with the options widget."""
    page_as_admin.goto(f"{FRONTEND}{ADD_POLL}")
    _open_tab(page_as_admin, "Voting")
    page_as_admin.wait_for_selector(".poll-options-widget")
    shot.capture("poll-add-voting", element=page_as_admin.locator(ADD_FORM))


def test_poll_add_results(page_as_admin, shot) -> None:
    """The Results tab of the add form."""
    page_as_admin.goto(f"{FRONTEND}{ADD_POLL}")
    _open_tab(page_as_admin, "Results")
    page_as_admin.wait_for_selector("text=Show partial results")
    shot.capture("poll-add-results", element=page_as_admin.locator(ADD_FORM))


def test_poll_block_settings(page_as_admin, shot) -> None:
    """The home page in the editor, with a Poll block's settings open."""
    page_as_admin.goto(f"{FRONTEND}/edit")
    block = page_as_admin.locator(".block-editor-poll:not(.contained)").first
    block.wait_for()
    # Clicking the block's corner selects it without following the poll link.
    block.click(position={"x": 20, "y": 20})
    page_as_admin.wait_for_selector("text=Which poll")
    # The sidebar alone: selecting the block scrolls the page by an amount
    # that varies between runs, so a whole-window capture never repeats.
    shot.capture(
        "poll-block-settings",
        element=page_as_admin.locator(".sidebar-container"),
    )
