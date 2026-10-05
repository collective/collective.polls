from . import PORTAL_TYPE
from collective.polls.content.poll import IPoll
from collective.polls.content.poll import Poll
from plone.dexterity.fti import DexterityFTI
from zope.component import createObject

import pytest


class TestPollFTI:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, get_fti) -> None:
        self.portal = portal
        self.fti: DexterityFTI = get_fti(PORTAL_TYPE)

    @pytest.mark.parametrize(
        "attr,expected",
        [
            ("title", "Poll"),
            ("description", "A poll"),
            ("klass", "collective.polls.content.poll.Poll"),
            ("schema", "collective.polls.content.poll.IPoll"),
            ("add_permission", "collective.polls.AddPoll"),
            ("global_allow", True),
            ("filter_content_types", True),
            ("allowed_content_types", ("Image",)),
            ("allow_discussion", False),
            ("icon_expr", ""),
            ("default_view", "view"),
        ],
    )
    def test_fti(self, attr: str, expected):
        """FTI values."""
        assert isinstance(self.fti, DexterityFTI)
        assert getattr(self.fti, attr) == expected

    @pytest.mark.parametrize(
        "idx,behavior",
        enumerate((
            "plone.basic",
            "plone.namefromtitle",
            "volto.preview_image_link",
            "plone.shortname",
            "plone.excludefromnavigation",
        )),
    )
    def test_behaviors(self, idx: int, behavior: str):
        """Behaviors are present and in this order."""
        assert self.fti.behaviors[idx] == behavior

    def test_behaviors_count(self):
        """No other behavior is enabled."""
        assert len(self.fti.behaviors) == 5

    def test_schema(self):
        """The FTI points at IPoll."""
        assert self.fti.lookupSchema() == IPoll

    def test_factory(self):
        """The factory creates a Poll."""
        new_object = createObject(self.fti.factory)
        assert isinstance(new_object, Poll)
        assert IPoll.providedBy(new_object)
