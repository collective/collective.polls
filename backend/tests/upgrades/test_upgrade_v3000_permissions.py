"""Upgrade to 3000: anonymous visitors keep, or get back, their vote."""

from . import PORTAL_TYPE
from . import PROFILE
from . import SOURCE
from collective.polls.config import PERMISSION_VOTE
from collective.polls.upgrades.v3000 import permissions as step
from plone import api

import pytest


def anonymous_can_vote(poll) -> bool:
    return "Anonymous" in [
        r["name"] for r in poll.rolesOfPermission(PERMISSION_VOTE) if r["selected"]
    ]


class TestRestore:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, folder, run_step) -> None:
        self.portal = portal
        self.folder = folder
        self.run_step = run_step

    def make(self, state: str = "open", container=None, **fields):
        with api.env.adopt_roles(["Manager"]):
            poll = api.content.create(
                container or self.folder,
                PORTAL_TYPE,
                "poll",
                options=[{"description": "A"}, {"description": "B"}],
                **fields,
            )
            if state in ("open", "closed"):
                api.content.transition(obj=poll, transition="open")
            if state == "closed":
                api.content.transition(obj=poll, transition="close")
        return poll

    def wipe(self, poll) -> None:
        """What a 2.x reinstall did: reset the poll to the workflow's map."""
        api.portal.get_tool("portal_workflow").getWorkflowById(
            "poll_workflow"
        ).updateRoleMappingsFor(poll)

    def test_grant_restored(self):
        poll = self.make()
        self.wipe(poll)
        assert not anonymous_can_vote(poll)
        self.run_step(step.restore_anonymous_vote)
        assert anonymous_can_vote(poll)

    def test_twice(self):
        poll = self.make()
        self.wipe(poll)
        self.run_step(step.restore_anonymous_vote)
        self.run_step(step.restore_anonymous_vote)
        assert anonymous_can_vote(poll)

    @pytest.mark.parametrize(
        "state,fields",
        [("closed", {}), ("private", {}), ("open", {"allow_anonymous": False})],
    )
    def test_not_granted(self, state, fields):
        poll = self.make(state=state, **fields)
        self.wipe(poll)
        self.run_step(step.restore_anonymous_vote)
        assert not anonymous_can_vote(poll)

    def test_not_granted_in_private_folder(self):
        with api.env.adopt_roles(["Manager"]):
            hidden = api.content.create(self.portal, "Document", "hidden")
        poll = self.make(container=hidden)
        self.run_step(step.restore_anonymous_vote)
        assert not anonymous_can_vote(poll)


class TestReimportKeepsGrant:
    """Re-importing the workflow and rolemap leaves poll permissions alone."""

    @pytest.fixture(autouse=True)
    def _setup(self, folder, setup_tool, upgrade_steps) -> None:
        with api.env.adopt_roles(["Manager"]):
            self.poll = api.content.create(
                folder,
                PORTAL_TYPE,
                "poll",
                options=[{"description": "A"}, {"description": "B"}],
            )
            api.content.transition(obj=self.poll, transition="open")
        assert anonymous_can_vote(self.poll)
        setup_tool.setLastVersionForProfile(PROFILE, SOURCE)
        self.setup_tool = setup_tool
        self.steps = upgrade_steps()

    def test_after_reimport(self):
        """Checked before the step that restores the grant runs."""
        depends = self.steps[0]
        assert "Re-apply" in depends["title"]
        with api.env.adopt_roles(["Manager"]):
            depends["step"].doStep(self.setup_tool)
        assert anonymous_can_vote(self.poll)

    def test_after_upgrade(self):
        with api.env.adopt_roles(["Manager"]):
            for info in self.steps:
                info["step"].doStep(self.setup_tool)
        assert anonymous_can_vote(self.poll)
