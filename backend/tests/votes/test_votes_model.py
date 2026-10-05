"""Model-based test: a plain-Python reference model against a real poll.

Seeded random sequences of operations -- member votes, anonymous votes with
and without the cookie, repeat votes, invalid options, and the transitions
that matter (close, reopen, reject, open) -- run against both. After every
step, outcome, counts and voters must agree.
"""

from AccessControl import Unauthorized
from collective.polls.interfaces import AlreadyVoted
from collective.polls.interfaces import IPollVotes
from plone import api
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from random import Random

import pytest


MEMBERS = ("alice", "bob", "carol")
VISITORS = ("v1", "v2", "v3")
OPTION_IDS = (0, 1, 2)
INVALID = (7, -1)
STEPS = 60


class Model:
    """What the poll should do, in plain Python."""

    def __init__(self) -> None:
        self.state = "open"
        self.counts = dict.fromkeys(OPTION_IDS, 0)
        self.voters: set[str] = set()
        #: visitor -> anonymous voter id, once their browser holds a cookie
        self.jars: dict[str, str] = {}

    def vote(self, voter_id: str | None, option: int) -> str:
        if self.state != "open":
            return "unauthorized"
        if voter_id is not None and voter_id in self.voters:
            return "already"
        if option not in OPTION_IDS:
            return "false"
        return "ok"

    def record(self, voter_id: str, option: int) -> None:
        self.voters.add(voter_id)
        self.counts[option] += 1

    def transition(self, name: str) -> bool:
        allowed = {
            ("open", "close"): "closed",
            ("closed", "open"): "open",
            ("open", "reject"): "private",
            ("private", "open"): "open",
        }
        if (self.state, name) not in allowed:
            return False
        if name == "reject":
            self.counts = dict.fromkeys(OPTION_IDS, 0)
            self.voters = set()
        self.state = allowed[(self.state, name)]
        return True


def _outcome(func, *args) -> str:
    try:
        return "ok" if func(*args) else "false"
    except AlreadyVoted:
        return "already"
    except Unauthorized:
        return "unauthorized"


@pytest.fixture
def members(portal):
    for name in MEMBERS:
        api.user.create(
            email=f"{name}@example.org", username=name, password="secret12345"
        )
    return MEMBERS


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 6, 7, 8])
def test_model(poll, members, http_request, seed: int):
    rng = Random(seed)
    model = Model()
    request = http_request
    logout()
    for _ in range(STEPS):
        kind = rng.choice(("member", "member", "anon", "anon", "transition"))
        option = rng.choice(OPTION_IDS + INVALID)
        if kind == "member":
            name = rng.choice(members)
            expected = model.vote(name, option)
            with api.env.adopt_user(username=name):
                got = _outcome(poll.setVote, option, request)
            if expected == "ok":
                model.record(name, option)
        elif kind == "anon":
            visitor = rng.choice(VISITORS)
            request.cookies.clear()
            request.response.cookies.clear()
            if visitor in model.jars:
                cookie_value = model.jars[visitor].removeprefix("Anonymous-")
                request.cookies[f"collective.poll.{poll.UID()}"] = cookie_value
            expected = model.vote(model.jars.get(visitor), option)
            got = _outcome(poll.setVote, option, request)
            if expected == "ok":
                cookie = request.response.cookies[f"collective.poll.{poll.UID()}"]
                voter_id = f"Anonymous-{cookie['value']}"
                model.jars[visitor] = voter_id
                model.record(voter_id, option)
        else:
            name = rng.choice(("close", "open", "reject"))
            expected_ok = model.transition(name)
            with api.env.adopt_user(username=SITE_OWNER_NAME):
                wt = api.portal.get_tool("portal_workflow")
                possible = [t["id"] for t in wt.getTransitionsFor(poll)]
                if name in possible:
                    wt.doActionFor(poll, name)
            got = "ok" if name in possible else "false"
            expected = "ok" if expected_ok else "false"
        assert got == expected, (seed, kind, option, model.state)
        assert api.content.get_state(obj=poll) == model.state
        assert IPollVotes(poll).counts() == model.counts
        assert set(poll.voters()) == model.voters
