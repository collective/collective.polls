"""Fixtures for the screenshot scripts.

The scripts drive the development site of this repository, with its example
content, so the images agree with the tutorial. Start it first, from the
repository root::

    make backend-create-site   # once
    make backend-start
    make frontend-start

The scripts only read: none of them votes, edits, or saves, so running them
leaves the site as it was.
"""

import json
import urllib.error
import urllib.request
from collections.abc import Iterator

import pytest

from .shot import HEIGHT, WIDTH, Shot

#: The Volto frontend.
FRONTEND = "http://localhost:3000"

#: The Plone site, for the REST API.
BACKEND = "http://localhost:8080/Plone"

#: The development site's credentials, public by design.
ADMIN = ("admin", "admin")


def _token(login: str, password: str) -> str:
    """Sign in through the REST API and return a JSON web token.

    :param login: User name.
    :param password: Password.
    :returns: The token.
    :raises RuntimeError: When the site refuses the credentials.
    """
    request = urllib.request.Request(
        f"{BACKEND}/@login",
        data=json.dumps({"login": login, "password": password}).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            token = json.load(response).get("token")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"The site refused {login!r}: HTTP {error.code}") from error
    if not token:
        raise RuntimeError(f"The site returned no token for {login!r}")
    return token


def _reachable(url: str) -> bool:
    """Report whether a server answers at all.

    :param url: The address to try.
    :returns: ``True`` when it responds without a server error.
    """
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status < 500
    except OSError:
        return False


@pytest.fixture(scope="session", autouse=True)
def development_site() -> None:
    """Skip the whole run when the development site is not up.

    A server that is not running is a setup problem, not a failure of these
    scripts, and a wall of connection errors hides that.
    """
    missing = [url for url in (BACKEND, FRONTEND) if not _reachable(url)]
    if missing:
        pytest.skip(
            f"Nothing answers at {', '.join(missing)}. Start the development "
            f"site with `make backend-start` and `make frontend-start`."
        )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Pin the viewport and the language, so every capture is framed the same.

    :param browser_context_args: Playwright's own defaults.
    :returns: The arguments with the viewport and locale set.
    """
    return {
        **browser_context_args,
        "viewport": {"width": WIDTH, "height": HEIGHT},
        "locale": "en-US",
    }


@pytest.fixture
def anonymous_page(page):
    """A page with nobody signed in, as a visitor sees the site.

    :param page: Playwright's page fixture.
    :returns: The page.
    """
    return page


@pytest.fixture
def page_as_admin(page) -> Iterator:
    """A page signed in as the site administrator.

    Volto reads the token from the ``auth_token`` cookie, so setting it signs
    in without depending on the login form's markup.

    :param page: Playwright's page fixture.
    :returns: The page, signed in.
    :raises RuntimeError: When the page still offers to log in.
    """
    token = _token(*ADMIN)
    page.context.add_cookies(
        [
            {"name": "auth_token", "value": token, "url": FRONTEND},
        ]
    )
    page.goto(FRONTEND)
    page.wait_for_load_state("networkidle")
    # An anonymous page renders too: prove the sign in took.
    if page.locator("a[href^='/login']").count():
        raise RuntimeError(
            "Signed in as admin, and the page still offers a login link: the "
            "capture would be of an anonymous page."
        )
    yield page


@pytest.fixture
def shot(page) -> Shot:
    """Writes captures for this script.

    :param page: Playwright's page fixture.
    :returns: The recorder.
    """
    return Shot(page=page)
