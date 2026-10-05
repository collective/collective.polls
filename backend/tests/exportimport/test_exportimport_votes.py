"""A closed poll's votes go out with plone.exportimport, and come back in."""

from . import EXPORT_VOTES_KEY
from . import EXPORTED
from collective.polls.interfaces import IPollVotes
from collective.polls.serializers.exportimport import ExportPollSerializer
from collective.polls.serializers.exportimport import ImportPollDeserializer
from pathlib import Path
from plone import api
from plone.exportimport.exporters import get_exporter
from plone.exportimport.importers import get_importer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter

import json
import pytest


class TestSerializer:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, exportimport_request) -> None:
        self.make_poll = make_poll
        self.request = exportimport_request

    def serialize(self, poll) -> dict:
        serializer = getMultiAdapter((poll, self.request), ISerializeToJson)
        assert isinstance(serializer, ExportPollSerializer)
        return serializer(include_items=False)

    def test_closed_poll(self):
        data = self.serialize(self.make_poll())
        assert data[EXPORT_VOTES_KEY] == EXPORTED
        assert data["options"]

    def test_closed_poll_without_votes(self):
        data = self.serialize(self.make_poll(voters={}))
        assert data[EXPORT_VOTES_KEY] == {"counts": {}, "voters": []}

    def test_closed_poll_keeps_removed_options(self):
        """Votes for an option removed after voting are exported too."""
        poll = self.make_poll()
        IPollVotes(poll).merge({7: 4}, ["old-voter"])
        data = self.serialize(poll)
        assert data[EXPORT_VOTES_KEY]["counts"] == {"0": 2, "1": 1, "7": 4}
        assert "old-voter" in data[EXPORT_VOTES_KEY]["voters"]

    @pytest.mark.parametrize("state", ["private", "open"])
    def test_poll_not_closed(self, state):
        data = self.serialize(self.make_poll(state=state))
        assert EXPORT_VOTES_KEY not in data


class TestDeserializer:
    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, exportimport_request) -> None:
        self.make_poll = make_poll
        self.request = exportimport_request

    def deserialize(self, poll, data: dict) -> None:
        deserializer = getMultiAdapter((poll, self.request), IDeserializeFromJson)
        assert isinstance(deserializer, ImportPollDeserializer)
        with api.env.adopt_roles(["Manager"]):
            deserializer(data=data)

    def test_writes_votes(self):
        poll = self.make_poll(state="private", voters={})
        self.deserialize(poll, {"title": "Imported", EXPORT_VOTES_KEY: EXPORTED})
        votes = IPollVotes(poll)
        assert poll.title == "Imported"
        assert votes.counts() == {0: 2, 1: 1, 2: 0}
        assert votes.voters() == ["Anonymous-xyz", "member-a", "member-b"]

    def test_replaces_votes(self):
        """Importing over an existing poll does not add the votes up."""
        poll = self.make_poll(state="private", voters={"someone": 2})
        IPollVotes(poll).merge({7: 4}, [])
        self.deserialize(poll, {EXPORT_VOTES_KEY: EXPORTED})
        votes = IPollVotes(poll)
        assert votes.stored() == {0: 2, 1: 1}
        assert not votes.has_voter("someone")

    def test_keeps_removed_options(self):
        poll = self.make_poll(state="private", voters={})
        payload = {"counts": {"0": 1, "7": 4}, "voters": ["a"]}
        self.deserialize(poll, {EXPORT_VOTES_KEY: payload})
        votes = IPollVotes(poll)
        assert votes.counts() == {0: 1, 1: 0, 2: 0}
        assert votes.orphans() == {7: 4}

    def test_reads_the_request_body(self):
        """Without ``data``, the payload comes from the request body."""
        poll = self.make_poll(state="private", voters={})
        self.request["BODY"] = json.dumps({EXPORT_VOTES_KEY: EXPORTED})
        deserializer = getMultiAdapter((poll, self.request), IDeserializeFromJson)
        with api.env.adopt_roles(["Manager"]):
            deserializer()
        assert IPollVotes(poll).counts() == {0: 2, 1: 1, 2: 0}

    def test_without_votes_leaves_them(self):
        poll = self.make_poll(state="private", voters={"someone": 2})
        self.deserialize(poll, {"title": "Imported"})
        assert IPollVotes(poll).stored() == {2: 1}


class TestAdaptersNeedTheMarker:
    """Outside plone.exportimport, plone.restapi's own adapters answer."""

    @pytest.fixture(autouse=True)
    def _setup(self, make_poll, http_request) -> None:
        self.poll = make_poll()
        self.request = http_request

    def test_serializer(self):
        serializer = getMultiAdapter((self.poll, self.request), ISerializeToJson)
        assert not isinstance(serializer, ExportPollSerializer)
        assert EXPORT_VOTES_KEY not in serializer(include_items=False)

    def test_deserializer(self):
        deserializer = getMultiAdapter((self.poll, self.request), IDeserializeFromJson)
        assert not isinstance(deserializer, ImportPollDeserializer)


class TestRoundTrip:
    """Export a site, remove the poll, import the export: the votes are back."""

    @pytest.fixture(autouse=True)
    def _setup(self, portal, make_poll, no_commits, tmp_path) -> None:
        self.portal = portal
        poll = make_poll()
        self.uid = api.content.get_uuid(poll)
        get_exporter(portal).export_site(tmp_path)
        self.path = tmp_path
        with api.env.adopt_roles(["Manager"]):
            api.content.delete(poll)

    def exported(self) -> dict:
        metadata = json.loads((self.path / "content" / "__metadata__.json").read_text())
        filename = next(name for name in metadata["_data_files_"] if self.uid in name)
        return json.loads(Path(self.path / "content" / filename).read_text())

    def test_export(self):
        assert self.exported()[EXPORT_VOTES_KEY] == EXPORTED

    def test_import(self):
        with api.env.adopt_roles(["Manager"]):
            get_importer(self.portal).import_site(self.path)
        poll = api.content.get(UID=self.uid)
        assert api.content.get_state(poll) == "closed"
        votes = IPollVotes(poll)
        assert votes.counts() == {0: 2, 1: 1, 2: 0}
        assert votes.voters() == ["Anonymous-xyz", "member-a", "member-b"]
