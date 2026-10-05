"""Which transitions are allowed, and to whom. Ported from the legacy suite."""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.WorkflowCore import WorkflowException

import pytest


class TestWorkflowTransitions:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, wt, poll) -> None:
        self.portal = portal
        self.wt = wt
        self.obj = poll

    def _state(self) -> str:
        return self.wt.getInfoFor(self.obj, "review_state")

    def test_initial_state(self):
        assert self._state() == "private"

    def test_all_stages(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.wt.doActionFor(self.obj, "submit")
        assert self._state() == "pending"
        self.wt.doActionFor(self.obj, "open")
        assert self._state() == "open"
        self.wt.doActionFor(self.obj, "close")
        assert self._state() == "closed"

    def test_direct(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.wt.doActionFor(self.obj, "open")
        assert self._state() == "open"
        self.wt.doActionFor(self.obj, "close")
        assert self._state() == "closed"

    def test_polls_can_be_reopened(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        for _ in range(2):
            self.wt.doActionFor(self.obj, "open")
            assert self._state() == "open"
            self.wt.doActionFor(self.obj, "close")
            assert self._state() == "closed"

    def test_transitions_not_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # A private poll cannot be closed
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "close")
        self.wt.doActionFor(self.obj, "submit")
        assert self._state() == "pending"
        # Nor can a pending one
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "close")
        # It can be retracted
        self.wt.doActionFor(self.obj, "retract")
        assert self._state() == "private"
        self.wt.doActionFor(self.obj, "open")
        # An open poll cannot be retracted nor submitted
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "retract")
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "submit")
        # It can be rejected back to private
        self.wt.doActionFor(self.obj, "reject")
        assert self._state() == "private"
        self.wt.doActionFor(self.obj, "open")
        self.wt.doActionFor(self.obj, "close")
        assert self._state() == "closed"
        # A closed poll can only be reopened
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "retract")
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "submit")
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "reject")

    def test_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        # open is guarded by Review portal content
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "open")
        self.wt.doActionFor(self.obj, "submit")
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "open")
        # A Reviewer can retract and open
        setRoles(self.portal, TEST_USER_ID, ["Reviewer"])
        self.wt.doActionFor(self.obj, "retract")
        self.wt.doActionFor(self.obj, "open")
        # Only Manager, Site Administrator and Reviewer can close it
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "close")
        setRoles(
            self.portal, TEST_USER_ID, ["Owner", "Member", "Contributor", "Editor"]
        )
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "close")
        # ... or send it back
        with pytest.raises(WorkflowException):
            self.wt.doActionFor(self.obj, "reject")
        setRoles(self.portal, TEST_USER_ID, ["Reviewer"])
        self.wt.doActionFor(self.obj, "reject")
        self.wt.doActionFor(self.obj, "open")
        self.wt.doActionFor(self.obj, "close")
        assert self._state() == "closed"

    @pytest.mark.parametrize(
        "role,allowed",
        [
            ("Manager", True),
            ("Site Administrator", True),
            ("Reviewer", True),
            ("Editor", False),
            ("Contributor", False),
            ("Member", False),
        ],
    )
    def test_close_by_role(self, role: str, allowed: bool):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.wt.doActionFor(self.obj, "open")
        setRoles(self.portal, TEST_USER_ID, [role])
        transitions = [t["id"] for t in self.wt.getTransitionsFor(self.obj)]
        assert ("close" in transitions) is allowed
