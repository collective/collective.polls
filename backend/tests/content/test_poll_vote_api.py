"""The 3.0 details of ``Poll.setVote``: the cookie, ``AlreadyVoted``, ids."""

from collective.polls.config import COOKIE_MAX_AGE
from collective.polls.interfaces import AlreadyVoted
from plone.app.testing import logout

import pytest


class TestVoteApi:
    @pytest.fixture(autouse=True)
    def _setup(self, polls, http_request) -> None:
        self.p2 = polls["p2"]
        self.p3 = polls["p3"]
        self.request = http_request

    def _cookie(self) -> dict:
        return self.request.response.cookies[f"collective.poll.{self.p3.UID()}"]

    def test_second_vote_raises_already_voted(self):
        self.p2.setVote(0)
        with pytest.raises(AlreadyVoted):
            self.p2.setVote(1)

    def test_anonymous_without_request_raises_already_voted(self):
        """Nothing to tell by, so the visitor counts as having voted."""
        logout()
        with pytest.raises(AlreadyVoted):
            self.p3.setVote(0)

    @pytest.mark.parametrize("option", [True, False])
    def test_bool_is_not_an_option(self, option):
        """``True == 1`` in Python; it is still not an option id."""
        assert self.p2.setVote(option) is False
        assert self.p2.total_votes == 0

    def test_member_gets_no_cookie(self):
        self.p3.setVote(0, self.request)
        assert self.request.response.cookies == {}

    @pytest.mark.parametrize(
        "attr,value",
        [
            ("Path", "/"),
            ("Max-Age", str(COOKIE_MAX_AGE)),
            ("SameSite", "Lax"),
        ],
    )
    def test_cookie_attributes(self, attr: str, value: str):
        logout()
        self.p3.setVote(0, self.request)
        assert self._cookie()[attr] == value

    def test_cookie_readable_by_scripts_and_no_expires(self):
        """No HttpOnly: the browser reads it. No fixed expiry date anymore."""
        logout()
        self.p3.setVote(0, self.request)
        assert "HttpOnly" not in self._cookie()
        assert "Expires" not in self._cookie()

    @pytest.mark.parametrize(
        "server_url,secure",
        [
            ("http://nohost", False),
            ("https://example.org", True),
        ],
    )
    def test_cookie_secure_on_https(self, server_url: str, secure: bool):
        self.request["SERVER_URL"] = server_url
        logout()
        self.p3.setVote(0, self.request)
        assert bool(self._cookie().get("Secure")) is secure

    def test_voters_sorted(self):
        self.p3.setVote(0, self.request)
        logout()
        self.p3.setVote(1, self.request)
        voters = self.p3.voters()
        assert voters == sorted(voters)
        assert len(voters) == 2
