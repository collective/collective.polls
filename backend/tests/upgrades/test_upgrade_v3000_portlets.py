"""Upgrade to 3000: the 2.x vote portlet goes, every assignment of it too."""

from collective.polls.portlet.voteportlet import Assignment
from collective.polls.upgrades.v3000 import portlets as step
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.storage import PortletAssignmentMapping
from plone.portlets.utils import registerPortletType
from ZODB.broken import Broken
from ZODB.broken import find_global
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility

import pytest


def category_mapping(manager_name: str, category: str, key: str):
    """Create the assignment mapping of a user, group or type.

    Plone creates every manager with its three categories, empty.
    """
    manager = getUtility(IPortletManager, name=manager_name)
    mapping = PortletAssignmentMapping(
        manager=manager_name, category=category, name=key
    )
    manager[category][key] = mapping
    return manager[category][key]


class TestRemove:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, folder, run_step) -> None:
        registerPortletType(
            portal,
            title="Voting portlet",
            description="A portlet to allow voting on a specific poll",
            addview=step.PORTLET_TYPE,
        )
        left = getUtility(IPortletManager, name="plone.leftcolumn")
        self.mappings = {
            "root": getMultiAdapter((portal, left), IPortletAssignmentMapping),
            "folder": getMultiAdapter((folder, left), IPortletAssignmentMapping),
            "dashboard": category_mapping("plone.dashboard1", USER_CATEGORY, "member"),
            "group": category_mapping("plone.rightcolumn", GROUP_CATEGORY, "staff"),
            "type": category_mapping(
                "plone.rightcolumn", CONTENT_TYPE_CATEGORY, "Document"
            ),
        }
        for mapping in self.mappings.values():
            mapping["vote"] = Assignment()
            mapping["other"] = navigation.Assignment()
        #: What each mapping must hold afterwards: everything but the vote.
        self.expected = {
            where: [key for key in mapping if key != "vote"]
            for where, mapping in self.mappings.items()
        }
        self.run_step = run_step

    @pytest.mark.parametrize("where", ["root", "folder", "dashboard", "group", "type"])
    def test_assignments_removed(self, where):
        self.run_step(step.remove_vote_portlets)
        assert "other" in self.expected[where]
        assert list(self.mappings[where].keys()) == self.expected[where]

    def test_type_unregistered(self):
        assert queryUtility(IPortletType, name=step.PORTLET_TYPE) is not None
        self.run_step(step.remove_vote_portlets)
        assert queryUtility(IPortletType, name=step.PORTLET_TYPE) is None

    def test_twice(self):
        self.run_step(step.remove_vote_portlets)
        self.run_step(step.remove_vote_portlets)
        assert list(self.mappings["root"].keys()) == self.expected["root"]

    def test_many_objects(self, monkeypatch):
        """Savepoints between batches do not lose anything."""
        monkeypatch.setattr(step, "BATCH_SIZE", 1)
        self.run_step(step.remove_vote_portlets)
        assert list(self.mappings["folder"].keys()) == self.expected["folder"]


def test_broken_assignment_recognized():
    """Without the class, an assignment loads broken; it is still found."""
    cls = find_global(
        "collective.polls.portlet.voteportlet", "NoSuchClass", Broken=Broken
    )
    assert step.is_vote_assignment(cls())


def test_other_assignment_not_recognized():
    assert not step.is_vote_assignment(navigation.Assignment())
