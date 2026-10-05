"""The shape of ``poll_workflow``: states, transitions, and that it closes."""

from . import INITIAL_STATE
from . import MANAGED_PERMISSIONS
from . import PORTAL_TYPE
from . import STATES
from . import TRANSITIONS
from . import WORKFLOW_ID
from plone import api

import pytest


class TestWorkflowDefinition:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        self.wt = api.portal.get_tool("portal_workflow")
        self.workflow = self.wt[WORKFLOW_ID]

    def test_installed(self):
        assert WORKFLOW_ID in self.wt.getWorkflowIds()

    def test_bound_to_poll(self):
        assert self.wt.getChainForPortalType(PORTAL_TYPE) == (WORKFLOW_ID,)

    def test_initial_state(self):
        assert self.workflow.initial_state == INITIAL_STATE

    def test_states(self):
        assert sorted(self.workflow.states.objectIds()) == sorted(STATES)

    def test_transitions(self):
        assert sorted(self.workflow.transitions.objectIds()) == sorted(TRANSITIONS)

    def test_managed_permissions(self):
        assert sorted(self.workflow.permissions) == sorted(MANAGED_PERMISSIONS)

    @pytest.mark.parametrize("state_id", sorted(STATES))
    def test_exit_transitions(self, state_id: str):
        state = self.workflow.states[state_id]
        assert sorted(state.transitions) == sorted(STATES[state_id])

    @pytest.mark.parametrize("transition_id", sorted(TRANSITIONS))
    def test_transition_target_and_guard(self, transition_id: str):
        transition = self.workflow.transitions[transition_id]
        new_state, guard = TRANSITIONS[transition_id]
        assert transition.new_state_id == new_state
        assert transition.getGuard().permissions == (guard,)

    def test_every_state_reachable(self):
        """Walking the exits from the initial state reaches every state."""
        seen = {INITIAL_STATE}
        pending = [INITIAL_STATE]
        while pending:
            state = self.workflow.states[pending.pop()]
            for transition_id in state.transitions:
                target = self.workflow.transitions[transition_id].new_state_id
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        assert seen == set(STATES)

    def test_no_dead_end(self):
        """Every state has a way out; ``closed`` only back to ``open``."""
        for state_id in STATES:
            assert self.workflow.states[state_id].transitions
        assert self.workflow.states["closed"].transitions == ("open",)
