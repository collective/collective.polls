"""``POST @vote``: every outcome of the contract, and what it writes."""

from . import COOKIE_KEY
from collective.polls.config import COOKIE_MAX_AGE
from collective.polls.interfaces import IPollVotes

import pytest


class TestVote:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, validate, reload) -> None:
        self.poll = make_poll()
        self.session_for = session_for
        self.validate = validate
        self.reload = reload

    def vote(self, username: str, body: object):
        return self.session_for(username).post("polls/poll/@vote", json=body)

    def test_member(self):
        response = self.vote("member", {"option_id": 1})
        assert response.status_code == 200, response.text
        assert response.headers["Cache-Control"] == "private, no-store"
        assert "Set-Cookie" not in response.headers
        data = self.validate(response.json())
        assert data["has_voted"] is True
        assert data["total_votes"] == 1
        assert data["results"][1]["votes"] == 1
        poll = self.reload(self.poll)
        assert IPollVotes(poll).voters() == ["member"]

    def test_anonymous(self):
        """Anonymous votes commit, with no CSRF token to send."""
        response = self.vote("anonymous", {"option_id": 0})
        assert response.status_code == 200, response.text
        data = self.validate(response.json())
        assert data["has_voted"] is True
        poll = self.reload(self.poll)
        assert IPollVotes(poll).counts() == {0: 1, 1: 0}
        [voter] = IPollVotes(poll).voters()
        assert voter.startswith("Anonymous-")

    def test_anonymous_cookie(self):
        response = self.vote("anonymous", {"option_id": 0})
        cookie = response.headers["Set-Cookie"]
        name, _, attributes = cookie.partition(";")
        key, _, value = name.partition("=")
        assert key == f"{COOKIE_KEY}{self.poll.UID()}"
        poll = self.reload(self.poll)
        assert IPollVotes(poll).voters() == [f"Anonymous-{value.strip(chr(34))}"]
        parts = {
            p.strip().split("=")[0].lower(): p.strip() for p in attributes.split(";")
        }
        assert parts["path"] == "Path=/"
        assert parts["max-age"] == f"Max-Age={COOKIE_MAX_AGE}"
        assert parts["samesite"] == "SameSite=Lax"
        assert "httponly" not in parts
        assert "secure" not in parts

    def test_anonymous_twice_with_cookie(self):
        session = self.session_for("anonymous")
        assert session.post("polls/poll/@vote", json={"option_id": 0}).ok
        response = session.post("polls/poll/@vote", json={"option_id": 1})
        assert response.status_code == 403
        assert response.json()["error"]["type"] == "AlreadyVoted"
        assert IPollVotes(self.reload(self.poll)).total() == 1

    def test_anonymous_twice_without_cookie(self):
        """A documented limitation: the cookie is the only way to tell."""
        assert self.vote("anonymous", {"option_id": 0}).ok
        assert self.vote("anonymous", {"option_id": 1}).ok
        assert IPollVotes(self.reload(self.poll)).total() == 2

    def test_modified_changes(self):
        before = self.poll.modified()
        assert self.vote("member", {"option_id": 0}).ok
        assert self.reload(self.poll).modified() > before


class TestRefused:
    """Every error leaves the poll as it was."""

    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, reload) -> None:
        self.make_poll = make_poll
        self.session_for = session_for
        self.reload = reload

    def assert_untouched(self, poll, votes: int = 0) -> None:
        before = poll.modified()
        poll = self.reload(poll)
        assert IPollVotes(poll).total() == votes
        assert poll.modified() == before

    @pytest.mark.parametrize(
        "kwargs",
        [
            {},
            {"data": "not json"},
            {"json": {}},
            {"json": {"option": 0}},
            {"json": {"option_id": "0"}},
            {"json": {"option_id": 0.5}},
            {"json": {"option_id": True}},
            {"json": {"option_id": None}},
            {"json": {"option_id": [0]}},
            {"json": [0]},
            {"json": 0},
        ],
        ids=[
            "no-body",
            "not-json",
            "empty",
            "wrong-key",
            "string",
            "float",
            "bool",
            "null",
            "list-id",
            "list-body",
            "number-body",
        ],
    )
    def test_bad_body(self, kwargs):
        poll = self.make_poll()
        response = self.session_for("member").post("polls/poll/@vote", **kwargs)
        assert response.status_code == 400
        assert response.headers["Cache-Control"] == "private, no-store"
        error = response.json()["error"]
        assert error["type"] == "BadRequest"
        assert "option_id" in error["message"]
        self.assert_untouched(poll)

    @pytest.mark.parametrize("option_id", [2, -1, 99])
    def test_unknown_option(self, option_id):
        poll = self.make_poll()
        response = self.session_for("anonymous").post(
            "polls/poll/@vote", json={"option_id": option_id}
        )
        assert response.status_code == 400
        assert response.json()["error"] == {
            "type": "BadRequest",
            "message": "This poll has no such option.",
        }
        assert "Set-Cookie" not in response.headers
        self.assert_untouched(poll)

    def test_already_voted(self):
        poll = self.make_poll(voters={"member": 0})
        response = self.session_for("member").post(
            "polls/poll/@vote", json={"option_id": 1}
        )
        assert response.status_code == 403
        assert response.json()["error"] == {
            "type": "AlreadyVoted",
            "message": "You already voted in this poll.",
        }
        self.assert_untouched(poll, votes=1)

    @pytest.mark.parametrize(
        "username,state,fields",
        [
            ("anonymous", "open", {"allow_anonymous": False}),
            ("anonymous", "closed", {}),
            ("anonymous", "private", {}),
            ("member", "closed", {}),
            ("member", "pending", {}),
            ("manager", "private", {}),
        ],
    )
    def test_no_permission(self, username, state, fields):
        """plone.rest answers 401, for members too, with its own body."""
        poll = self.make_poll(state=state, **fields)
        response = self.session_for(username).post(
            "polls/poll/@vote", json={"option_id": 0}
        )
        assert response.status_code == 401
        assert response.json()["type"] == "Unauthorized"
        self.assert_untouched(poll)
