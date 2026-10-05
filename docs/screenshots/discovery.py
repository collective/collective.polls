"""Discover which screenshots the documentation references.

The list of screenshots is not maintained here. It is read from the Markdown
itself: keeping a second list would mean keeping it up to date, and it would
not stay so. A capture under a name no page references fails, so no orphan
image reaches the repository.
"""

import re
from functools import cache
from pathlib import Path

#: Root of the docs project.
ROOT = Path(__file__).resolve().parent.parent

#: The Markdown sources.
SOURCES = ROOT / "docs"

#: Where captures are written. The same path the Markdown references.
SCREENS = SOURCES / "_static" / "screens"

#: An ``image`` directive pointing at a screenshot, with its ``:alt:`` text.
IMAGE = re.compile(
    r"```\{image\}\s+/_static/screens/(?P<name>[\w-]+)\.png\s*\n"
    r"(?:[^`]*?:alt:\s*(?P<alt>[^\n]+))?",
)


@cache
def referenced() -> dict[str, str]:
    """List the screenshots the documentation references.

    :returns: ``{name: alt text}``, sorted by name, for every ``image``
        directive under ``/_static/screens/``.
    """
    found: dict[str, str] = {}
    for source in sorted(SOURCES.rglob("*.md")):
        if "_build" in source.parts:
            continue
        for match in IMAGE.finditer(source.read_text(encoding="utf-8")):
            found[match["name"]] = (match["alt"] or "").strip()
    return dict(sorted(found.items()))


def on_disk() -> set[str]:
    """List the screenshots in the screens directory.

    :returns: Their names, without extension.
    """
    return {path.stem for path in SCREENS.glob("*.png")}
