# Capturing the documentation's screenshots

The screenshots in this documentation are not captured by hand.
Scripts drive a browser with [Playwright](https://playwright.dev/python/), and write each screen into `docs/_static/screens/`, under the name the Markdown references.
When Volto or the add-on changes how a poll looks, one run brings every image up to date.

## Prepare

Install the dependencies and the browser, from the `docs` folder.

```shell
make screenshots-install
```

The scripts photograph the development site and its example content.
Start it from the repository root, creating the site on the first run.

```shell
make backend-create-site
make backend-start
make frontend-start
```

If either server is not answering, the run skips with a message that says so.

## Run

```shell
make screenshots
```

The scripts only read: they open the add form and the page editor without saving, and nobody votes.
Running them leaves the site as it was.

## The list lives in the Markdown

Which screenshots exist is read from the `image` directives under `/_static/screens/` in the documentation.
A capture under a name no page references fails, and three checks keep the two in step:

-   every image in `docs/_static/screens/` is referenced by a page;
-   every referenced image exists;
-   every referenced image has `:alt:` text.

## Writing a script

Add the `image` directive to the page first, then a script in `test_polls.py`.

```python
def test_poll_closed_results(anonymous_page, shot) -> None:
    """A closed poll's final results, which every visitor sees."""
    anonymous_page.goto(f"{FRONTEND}{CHOOSE_A_CAPTAIN}")
    anonymous_page.wait_for_selector(".poll-results-pie")
    shot.capture("poll-closed-results", element=anonymous_page.locator(".poll-view"))
```

Use `anonymous_page` for what a visitor sees, and `page_as_admin` for editing screens.
`page_as_admin` signs in by setting the token the REST API returns as Volto's `auth_token` cookie, and checks that the sign in took.

### Framing

`shot.capture` photographs the whole window, or one element with `element=`.
An element smaller than 300 by 150 pixels is refused: it means the selector matched the wrong element, such as the search box in the header.

### Stability

Before each capture, the page's animations, transitions, and blinking caret are turned off, the focus is cleared, and the network is left to settle.
Run the captures twice and compare the files: a capture that changes when nothing changed makes every pull request show a diff.
Crop to an element when the page's scroll position varies between runs, as it does in the block editor.

## Credentials

The development site's `admin` user, with the password `admin`.
Never point these scripts at a real site.
