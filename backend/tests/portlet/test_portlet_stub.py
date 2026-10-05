"""Stored 2.x vote portlet assignments still load."""

from collective.polls.portlet.voteportlet import Assignment
from plone.portlets.interfaces import IPortletAssignment

import pickle


def test_importable_at_legacy_path():
    assert Assignment.__module__ == "collective.polls.portlet.voteportlet"
    assert Assignment.__name__ == "Assignment"


def test_round_trip():
    """A pickle made with the 2.x attributes loads with them."""
    assignment = Assignment()
    assignment.__dict__.update(poll="abc", header="Vote!", show_closed=True)
    loaded = pickle.loads(pickle.dumps(assignment))  # noqa: S301
    assert type(loaded) is Assignment
    assert (loaded.poll, loaded.header, loaded.show_closed) == ("abc", "Vote!", True)


def test_defaults_and_title():
    assignment = Assignment()
    assert IPortletAssignment.providedBy(assignment)
    assert assignment.poll == "latest"
    assert assignment.title == "Voting portlet (removed)"
