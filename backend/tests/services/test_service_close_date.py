"""``@poll`` and ``@vote`` before and after a poll's closing date."""

from collective.polls.interfaces import IPollVotes
from collective.polls.serializers.poll import results_visible
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from plone import api

import pytest
import transaction


#: Three votes: two for "Yes", one for "No".
VOTERS = {"someone": 0, "someone-else": 0, "voter": 1}

PAST = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
FUTURE = datetime(2099, 12, 31, 23, 0, tzinfo=timezone.utc)


class TestPayload:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, validate) -> None:
        self.make_poll = make_poll
        self.session_for = session_for
        self.validate = validate

    def get(self, username: str, path: str = "polls/poll") -> dict:
        response = self.session_for(username).get(f"{path}/@poll")
        assert response.status_code == 200, response.text
        return self.validate(response.json())

    def test_no_closing_date(self):
        self.make_poll()
        data = self.get("anonymous")
        assert data["close_date"] is None
        assert data["expired"] is False

    def test_before(self):
        self.make_poll(voters=VOTERS, close_date=FUTURE)
        data = self.get("member")
        assert data["close_date"] == "2099-12-31T23:00:00+00:00"
        assert data["expired"] is False
        assert data["results"] is None

    @pytest.mark.parametrize("username", ["anonymous", "member", "voter"])
    @pytest.mark.parametrize("show_results", ["never", "after_vote", "always"])
    def test_after(self, username, show_results):
        """Past its closing date, a poll shows its results to everyone."""
        self.make_poll(voters=VOTERS, close_date=PAST, show_results=show_results)
        data = self.get(username)
        assert data["state"] == "open"
        assert data["expired"] is True
        assert data["total_votes"] == 3

    def test_in_utc(self):
        """Whatever timezone the date was saved in, the payload says UTC."""
        local = datetime(2026, 1, 1, 9, 0, tzinfo=timezone(timedelta(hours=-3)))
        self.make_poll(close_date=local)
        assert self.get("anonymous")["close_date"] == "2026-01-01T12:00:00+00:00"

    @pytest.mark.parametrize("state", ["private", "pending"])
    def test_not_open(self, state):
        """Before opening, a past closing date shows nobody the results."""
        self.make_poll(state=state, close_date=PAST)
        data = self.get("manager")
        assert data["expired"] is True
        assert data["state"] == state

    def test_not_open_hidden_from_member(self, reload):
        """Only the reviewer sees results of an unopened poll, expired or not."""
        poll = self.make_poll(state="private", close_date=PAST)
        with api.env.adopt_user(username="member"):
            assert results_visible(reload(poll), False) is False

    def test_anonymous_blocked_until_expired(self):
        """The warning about anonymous votes is moot once voting ended."""
        self.make_poll(container="hidden", close_date=PAST)
        assert self.get("manager", "hidden/poll")["anonymous_blocked"] is False


class TestVote:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, reload) -> None:
        self.make_poll = make_poll
        self.session_for = session_for
        self.reload = reload

    @pytest.mark.parametrize("username", ["anonymous", "member"])
    def test_refused(self, username):
        poll = self.make_poll(close_date=PAST)
        response = self.session_for(username).post(
            "polls/poll/@vote", json={"option_id": 0}
        )
        assert response.status_code == 403
        assert response.json()["error"] == {
            "type": "PollClosed",
            "message": "This poll is closed.",
        }
        assert IPollVotes(self.reload(poll)).total() == 0

    def test_refused_in_portuguese(self):
        api.portal.set_registry_record("plone.available_languages", ["en", "pt-br"])
        api.portal.set_registry_record("plone.use_request_negotiation", True)
        self.make_poll(close_date=PAST)
        response = self.session_for("member").post(
            "polls/poll/@vote",
            json={"option_id": 0},
            headers={"Accept-Language": "pt-br"},
        )
        assert response.json()["error"]["message"] == "Esta enquete está encerrada."

    def test_before(self):
        self.make_poll(close_date=FUTURE)
        response = self.session_for("member").post(
            "polls/poll/@vote", json={"option_id": 0}
        )
        assert response.status_code == 200, response.text


class TestEtag:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, reload) -> None:
        self.poll = make_poll(close_date=FUTURE)
        self.reload = reload
        self.anon = session_for("anonymous")

    def test_expiring_changes_etag(self):
        """A cached answer from before the closing date is stale after it."""
        before = self.anon.get("polls/poll/@poll").headers["ETag"]
        # Nothing stored changes when the date passes; moving the date has
        # the same effect without touching the modification date.
        poll = self.reload(self.poll)
        modified = poll.modified()
        poll.close_date = PAST
        transaction.commit()
        assert self.reload(self.poll).modified() == modified
        response = self.anon.get("polls/poll/@poll", headers={"If-None-Match": before})
        assert response.status_code == 200
        assert response.headers["ETag"].endswith('-open-expired"')
        assert response.json()["expired"] is True
