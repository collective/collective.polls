"""Polls created and edited through ``plone.restapi``'s own content API."""

from . import EXPORT_VOTES_KEY
from . import PORTAL_TYPE
from collective.polls.interfaces import IPollVotes

import pytest


#: Votes as plone.exportimport would write them.
VOTES_PAYLOAD = {"counts": {"0": 5, "1": 2}, "voters": ["member", "voter"]}


class TestCreate:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, session_for, reload) -> None:
        self.portal = portal
        self.session = session_for("manager")
        self.reload = reload

    def create(self, options: list) -> object:
        return self.session.post(
            "polls",
            json={"@type": PORTAL_TYPE, "title": "A poll", "options": options},
        )

    def test_ids_assigned(self):
        """The options subscriber sees the value plone.restapi stored."""
        response = self.create([{"description": "Yes"}, {"description": "No"}])
        assert response.status_code == 201, response.text
        expected = [
            {"option_id": 0, "description": "Yes"},
            {"option_id": 1, "description": "No"},
        ]
        assert response.json()["options"] == expected
        poll = self.reload("polls/a-poll")
        assert poll.options == expected

    @pytest.mark.parametrize(
        "options,message",
        [
            ([], "You need to provide at least two options for a poll."),
            (
                [{"description": "Yes"}],
                "You need to provide at least two options for a poll.",
            ),
            (
                [
                    {"option_id": 1, "description": "Yes"},
                    {"option_id": 1, "description": "No"},
                ],
                "Two options cannot share an id.",
            ),
        ],
        ids=["none", "one", "duplicate-ids"],
    )
    def test_invariant(self, options, message):
        response = self.create(options)
        assert response.status_code == 400
        assert message in response.json()["message"]
        assert "a-poll" not in self.reload("polls").objectIds()

    @pytest.mark.parametrize(
        "options",
        [
            ["Yes", "No"],
            [{"description": ""}, {"description": "No"}],
            [{"description": "Yes", "votes": 3}, {"description": "No"}],
        ],
        ids=["bare-strings", "empty-description", "extra-key"],
    )
    def test_json_schema(self, options):
        """Only ``{option_id?, description}`` objects pass over REST."""
        response = self.create(options)
        assert response.status_code == 400


class TestEdit:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, reload) -> None:
        self.make_poll = make_poll
        self.session = session_for("manager")
        self.reload = reload

    def test_new_option_gets_id(self):
        """The options subscriber sees the value plone.restapi stored on edit too."""
        poll = self.make_poll(state="private")
        options = [*poll.options, {"description": "Maybe"}]
        response = self.session.patch("polls/poll", json={"options": options})
        assert response.status_code == 204, response.text
        poll = self.reload(poll)
        assert poll.options[-1] == {"option_id": 2, "description": "Maybe"}

    @pytest.mark.parametrize("state", ["open", "closed"])
    def test_refused_while_votes_can_exist(self, state):
        """Options cannot change while votes exist: nobody may edit."""
        poll = self.make_poll(state=state)
        response = self.session.patch(
            "polls/poll", json={"options": [{"description": "Only"}]}
        )
        assert response.status_code == 401
        assert len(self.reload(poll).options) == 2


class TestVotesStayOutOfTheContentAPI:
    """Only plone.exportimport carries votes; the content API never does."""

    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, session_for, reload) -> None:
        self.make_poll = make_poll
        self.session = session_for("manager")
        self.reload = reload

    def test_get_closed_poll(self):
        self.make_poll(state="closed", voters={"member": 0, "voter": 1})
        response = self.session.get("polls/poll")
        assert response.status_code == 200
        assert EXPORT_VOTES_KEY not in response.json()

    def test_create_ignores_votes(self):
        response = self.session.post(
            "polls",
            json={
                "@type": PORTAL_TYPE,
                "title": "A poll",
                "options": [{"description": "Yes"}, {"description": "No"}],
                EXPORT_VOTES_KEY: VOTES_PAYLOAD,
            },
        )
        assert response.status_code == 201, response.text
        votes = IPollVotes(self.reload("polls/a-poll"))
        assert votes.stored() == {}
        assert votes.voters() == []

    def test_edit_ignores_votes(self):
        poll = self.make_poll(state="private")
        response = self.session.patch(
            "polls/poll", json={"title": "Edited", EXPORT_VOTES_KEY: VOTES_PAYLOAD}
        )
        assert response.status_code == 204, response.text
        poll = self.reload(poll)
        assert poll.title == "Edited"
        assert IPollVotes(poll).stored() == {}
        assert IPollVotes(poll).voters() == []


def test_types_widget(session_for):
    """Volto picks the options widget from the schema the API publishes."""
    response = session_for("manager").get(f"@types/{PORTAL_TYPE}")
    assert response.status_code == 200
    field = response.json()["properties"]["options"]
    assert field["widget"] == "poll_options"
    assert field["factory"] == "JSONField"
