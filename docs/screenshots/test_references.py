"""Keep the screenshots and the pages that show them in step.

These need no browser and no running site.
"""

import pytest

from .discovery import on_disk, referenced


@pytest.fixture(autouse=True, scope="module")
def development_site() -> None:
    """Run these checks without a running site."""


def test_every_screenshot_is_referenced() -> None:
    """No image in the screens directory is left without a page showing it."""
    orphans = sorted(on_disk() - set(referenced()))
    assert not orphans, f"Images no page references: {', '.join(orphans)}"


def test_every_reference_has_a_screenshot() -> None:
    """Every screenshot a page references exists."""
    missing = sorted(set(referenced()) - on_disk())
    assert not missing, f"Referenced, never captured: {', '.join(missing)}"


def test_every_reference_has_alt_text() -> None:
    """Every screenshot says what it shows, for readers who cannot see it."""
    bare = sorted(name for name, alt in referenced().items() if not alt)
    assert not bare, f"Screenshots without :alt: text: {', '.join(bare)}"
