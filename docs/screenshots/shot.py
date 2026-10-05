"""Write screenshots where and how the documentation expects them.

Two concerns live here. The first is where the file goes:
``docs/_static/screens/<name>.png``, under the name the Markdown references.
The second is stability: a capture that changes on every run produces a diff
when nothing changed, so :meth:`Shot.capture` turns off animations, waits for
the network to settle, and can mask elements.
"""

from collections.abc import Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page

# Playwright's timeout does not derive from the built-in TimeoutError.
from playwright.sync_api import TimeoutError as Timeout

from .discovery import SCREENS, referenced

#: Browser window width.
WIDTH = 1280

#: Browser window height.
HEIGHT = 800

#: Turns off transitions, animations, and the blinking caret: differences
#: between runs that are no change in the interface.
STABILIZE = """
*, *::before, *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
    caret-color: transparent !important;
    scroll-behavior: auto !important;
}
"""

#: Milliseconds to wait for the network to go quiet.
NETWORK_WAIT = 15_000

#: Smallest element worth a capture, in pixels. A crop smaller than this means
#: the selector matched the wrong element, such as the header's search box.
MIN_ELEMENT = (300, 150)

#: Covers masked elements; Playwright's default magenta draws the eye.
MASK_COLOUR = "#eceef0"


class UnknownScreenshot(RuntimeError):
    """A capture was asked for under a name no page references."""


class WrongElement(RuntimeError):
    """The element to crop to is too small to be the intended one."""


@dataclass
class Shot:
    """Writes captures for one script.

    :param page: The Playwright page to photograph.
    :param destination: Directory to write into.
    :param written: Names written during this run, in order.
    """

    page: Page
    destination: Path = SCREENS
    written: list[str] = field(default_factory=list)

    def _check(self, name: str) -> None:
        """Refuse a name the Markdown does not reference.

        :param name: Filename, without extension.
        :raises UnknownScreenshot: When no page references that name.
        """
        known = referenced()
        if name not in known:
            raise UnknownScreenshot(
                f"No page in docs/ references the screenshot {name!r}. "
                f"Referenced: {', '.join(known) or 'none'}."
            )

    def prepare(self) -> None:
        """Put the page into a reproducible state before photographing it."""
        self.page.add_style_tag(content=STABILIZE)
        self.page.mouse.move(0, 0)
        self.page.evaluate("() => document.activeElement?.blur?.()")
        with suppress(Timeout):
            self.page.wait_for_load_state("networkidle", timeout=NETWORK_WAIT)
        with suppress(Timeout, PlaywrightError):
            self.page.evaluate("() => document.fonts.ready")

    def capture(
        self,
        name: str,
        *,
        element: Locator | None = None,
        full_page: bool = False,
        mask: Sequence[Locator] | None = None,
    ) -> Path:
        """Photograph the page, or one element of it.

        :param name: Filename, without extension. Must be referenced by a page.
        :param element: Element to crop the capture to.
        :param full_page: Photograph the whole page, not only the window.
        :param mask: Elements to cover, such as dates that change between runs.
        :returns: The path written.
        :raises UnknownScreenshot: When no page references the name.
        :raises WrongElement: When the element is too small to be the subject.
        """
        self._check(name)
        self.prepare()
        target = self.destination / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        masks = list(mask or [])
        if element is not None:
            box = element.bounding_box()
            if box is None or (box["width"], box["height"]) < MIN_ELEMENT:
                raise WrongElement(
                    f"The element for {name!r} is {box and (box['width'], box['height'])}"
                    f" pixels, under {MIN_ELEMENT}: the selector matched the wrong one."
                )
            element.screenshot(path=target, mask=masks, mask_color=MASK_COLOUR)
        else:
            self.page.screenshot(
                path=target, full_page=full_page, mask=masks, mask_color=MASK_COLOUR
            )
        self.written.append(name)
        return target
