"""``GET @poll``: the payload per state and per caller, and its headers."""

from collective.polls.services.poll.get import etag_matches
from collective.polls.services.poll.get import PUBLIC_CACHE_CONTROL
from plone import api

import pytest
import transaction


#: Three votes: two for "Yes", one for "No".
VOTERS = {"someone": 0, "someone-else": 0, "voter": 1}

#: Results for ``VOTERS``.
RESULTS = [
    {
        "option_id": 0,
        "description": "Yes",
        "votes": 2,
        "percentage": 0.6666666666666666,
    },
    {
        "option_id": 1,
        "description": "No",
        "votes": 1,
        "percentage": 0.3333333333333333,
    },
]

#: Results with no votes at all.
NO_RESULTS = [
    {"option_id": 0, "description": "Yes", "votes": 0, "percentage": 0.0},
    {"option_id": 1, "description": "No", "votes": 0, "percentage": 0.0},
]


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

    def test_identity(self):
        poll = self.make_poll()
        data = self.get("anonymous")
        assert data["@id"] == f"{poll.absolute_url()}/@poll"
        assert data["uid"] == poll.UID()
        assert data["options"] == [
            {"option_id": 0, "description": "Yes"},
            {"option_id": 1, "description": "No"},
        ]
        assert data["allow_anonymous"] is True
        assert data["show_results"] is True
        assert data["results_graph"] == "bar"

    @pytest.mark.parametrize(
        "username,has_voted,results",
        [
            ("anonymous", None, RESULTS),
            ("member", False, None),
            ("voter", True, RESULTS),
            ("reviewer", False, RESULTS),
        ],
    )
    def test_open(self, username, has_voted, results):
        self.make_poll(voters=VOTERS)
        data = self.get(username)
        assert data["state"] == "open"
        assert data["can_vote"] is True
        assert data["has_voted"] is has_voted
        assert data["results"] == results
        assert data["total_votes"] == (3 if results else None)

    @pytest.mark.parametrize(
        "username,results",
        [
            ("anonymous", None),
            ("member", None),
            ("voter", None),
            ("reviewer", RESULTS),
        ],
    )
    def test_open_results_hidden(self, username, results):
        self.make_poll(voters=VOTERS, show_results=False)
        data = self.get(username)
        assert data["show_results"] is False
        assert data["results"] == results

    @pytest.mark.parametrize("username", ["anonymous", "member", "voter"])
    @pytest.mark.parametrize("show_results", [True, False])
    def test_closed(self, username, show_results):
        """Closed polls show their results to everyone."""
        self.make_poll(state="closed", voters=VOTERS, show_results=show_results)
        data = self.get(username)
        assert data["state"] == "closed"
        assert data["can_vote"] is False
        assert data["results"] == RESULTS
        assert data["total_votes"] == 3

    def test_closed_without_votes(self):
        self.make_poll(state="closed")
        data = self.get("anonymous")
        assert data["results"] == NO_RESULTS
        assert data["total_votes"] == 0

    @pytest.mark.parametrize("state", ["private", "pending"])
    def test_not_open_for_manager(self, state):
        self.make_poll(state=state)
        data = self.get("manager")
        assert data["state"] == state
        assert data["can_vote"] is False
        assert data["has_voted"] is False
        assert data["results"] == NO_RESULTS

    def test_private_hidden_from_member(self):
        self.make_poll(state="private")
        response = self.session_for("member").get("polls/poll/@poll")
        assert response.status_code == 401

    def test_private_hidden_from_anonymous(self):
        self.make_poll(state="private")
        response = self.session_for("anonymous").get("polls/poll/@poll")
        assert response.status_code == 401

    def test_results_in_option_order(self):
        options = [
            {"option_id": 1, "description": "No"},
            {"option_id": 0, "description": "Yes"},
        ]
        self.make_poll(voters=VOTERS, options=options)
        data = self.get("anonymous")
        assert [r["option_id"] for r in data["results"]] == [1, 0]
        assert [r["votes"] for r in data["results"]] == [1, 2]


class TestAnonymousBlocked:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for) -> None:
        self.make_poll = make_poll
        self.session = session_for("manager")

    def blocked(self, path: str) -> bool:
        return self.session.get(f"{path}/@poll").json()["anonymous_blocked"]

    def test_open_in_published_folder(self):
        self.make_poll()
        assert self.blocked("polls/poll") is False

    def test_open_in_private_folder(self):
        """The 2.x "publish the parent folder first" warning."""
        self.make_poll(container="hidden")
        assert self.blocked("hidden/poll") is True

    def test_not_for_anonymous_votes(self):
        self.make_poll(container="hidden", allow_anonymous=False)
        assert self.blocked("hidden/poll") is False

    def test_closed(self):
        self.make_poll(container="hidden", state="closed")
        assert self.blocked("hidden/poll") is False


class TestHeaders:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for) -> None:
        self.poll = make_poll()
        self.session_for = session_for
        self.anon = session_for("anonymous")

    def etag(self) -> str:
        return self.anon.get("polls/poll/@poll").headers["ETag"]

    def test_anonymous(self):
        response = self.anon.get("polls/poll/@poll")
        assert response.headers["Cache-Control"] == PUBLIC_CACHE_CONTROL
        assert response.headers["ETag"].startswith('"')
        assert response.headers["ETag"].endswith('-open"')

    @pytest.mark.parametrize(
        "header",
        ["{etag}", "*", "W/{etag}", '"other", {etag}'],
    )
    def test_not_modified(self, header):
        etag = self.etag()
        response = self.anon.get(
            "polls/poll/@poll", headers={"If-None-Match": header.format(etag=etag)}
        )
        assert response.status_code == 304
        assert response.content == b""
        assert response.headers["ETag"] == etag

    def test_modified(self):
        response = self.anon.get(
            "polls/poll/@poll", headers={"If-None-Match": '"other"'}
        )
        assert response.status_code == 200
        assert response.json()["state"] == "open"

    def test_vote_changes_etag(self):
        before = self.etag()
        response = self.session_for("member").post(
            "polls/poll/@vote", json={"option_id": 0}
        )
        assert response.status_code == 200
        assert self.etag() != before

    @pytest.mark.parametrize("via", ["rest", "api"])
    def test_transition_changes_etag(self, via, reload):
        """However the poll was closed, a cached "open" answer is stale."""
        before = self.etag()
        if via == "rest":
            response = self.session_for("manager").post("polls/poll/@workflow/close")
            assert response.status_code == 200
        else:
            with api.env.adopt_roles(["Manager"]):
                api.content.transition(obj=reload(self.poll), transition="close")
            transaction.commit()
        response = self.anon.get("polls/poll/@poll", headers={"If-None-Match": before})
        assert response.status_code == 200
        assert response.json()["state"] == "closed"

    @pytest.mark.parametrize("username", ["member", "manager"])
    def test_authenticated(self, username):
        response = self.session_for(username).get(
            "polls/poll/@poll", headers={"If-None-Match": self.etag()}
        )
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "private, no-store"
        assert "ETag" not in response.headers


class TestCachingProxy:
    """plone.app.caching, switched on, leaves the service's headers alone."""

    @pytest.fixture(autouse=True)
    def _setup(self, portal, make_poll, session_for) -> None:
        setup_tool = api.portal.get_tool("portal_setup")
        for profile in ("default", "with-caching-proxy"):
            setup_tool.runAllImportStepsFromProfile(
                f"profile-plone.app.caching:{profile}"
            )
        api.portal.set_registry_record(
            "plone.caching.interfaces.ICacheSettings.enabled", True
        )
        transaction.commit()
        make_poll()
        self.anon = session_for("anonymous")

    def test_caching_is_on(self):
        """Control: the content endpoint does get a caching rule."""
        response = self.anon.get("polls/poll")
        assert response.status_code == 200
        assert "X-Cache-Rule" in response.headers

    def test_poll_headers_kept(self):
        response = self.anon.get("polls/poll/@poll")
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == PUBLIC_CACHE_CONTROL
        assert "X-Cache-Rule" not in response.headers


@pytest.mark.parametrize(
    "header,expected",
    [
        ('"1-open"', True),
        ("1-open", True),
        ('W/"1-open"', True),
        ('"a", "1-open"', True),
        ("*", True),
        ('"1-closed"', False),
        ("", False),
    ],
)
def test_etag_matches(header, expected):
    assert etag_matches(header, '"1-open"') is expected
