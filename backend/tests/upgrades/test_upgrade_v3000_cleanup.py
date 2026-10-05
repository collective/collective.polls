"""Upgrade to 3000: 2.x tile and resource registrations go."""

from collective.polls.upgrades.v3000 import cleanup as step
from plone import api
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from zope.component import getUtility

import logging
import pytest


COVER_RECORD = "collective.cover.controlpanel.ICoverSettings.available_tiles"


def add_record(name: str, record_field, value) -> None:
    registry = getUtility(IRegistry)
    registry.records[name] = Record(record_field, value)


def list_field():
    return field.List(title="List", value_type=field.TextLine(title="Item"))


class TestTiles:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, run_step) -> None:
        self.registry = getUtility(IRegistry)
        self.run_step = run_step

    @pytest.mark.parametrize("name", ["plone.app.tiles", COVER_RECORD])
    def test_tile_removed(self, name):
        add_record(name, list_field(), ["other.tile", "collective.polls"])
        self.run_step(step.remove_legacy_registrations)
        assert self.registry[name] == ["other.tile"]

    @pytest.mark.parametrize("name", ["plone.app.tiles", COVER_RECORD])
    def test_record_without_tile(self, name):
        add_record(name, list_field(), ["other.tile"])
        self.run_step(step.remove_legacy_registrations)
        assert self.registry[name] == ["other.tile"]

    def test_records_absent(self):
        """Neither record exists on a site without tiles: nothing to do."""
        assert "plone.app.tiles" not in self.registry.records
        self.run_step(step.remove_legacy_registrations)
        assert "plone.app.tiles" not in self.registry.records
        assert COVER_RECORD not in self.registry.records


class TestResources:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, run_step) -> None:
        self.registry = getUtility(IRegistry)
        self.run_step = run_step

    def test_record_pointing_at_resource(self):
        name = "plone.resources/collective-polls.js"
        add_record(
            name, field.TextLine(title="JS"), "++resource++collective.polls/a.js"
        )
        self.run_step(step.remove_legacy_registrations)
        assert name not in self.registry.records

    def test_list_loses_only_our_entries(self):
        name = "plone.bundles/legacy.resources"
        add_record(
            name,
            list_field(),
            ["++resource++other/a.js", "++resource++collective.polls/b.js"],
        )
        self.run_step(step.remove_legacy_registrations)
        assert self.registry[name] == ["++resource++other/a.js"]

    def test_tuple_stays_a_tuple(self):
        name = "example.tuple"
        add_record(
            name,
            field.Tuple(title="Tuple", value_type=field.TextLine(title="Item")),
            ("keep", "++resource++collective.polls/b.css"),
        )
        self.run_step(step.remove_legacy_registrations)
        assert self.registry[name] == ("keep",)

    def test_other_records_untouched(self):
        before = {
            name: self.registry.records[name].value for name in self.registry.records
        }
        self.run_step(step.remove_legacy_registrations)
        after = {
            name: self.registry.records[name].value for name in self.registry.records
        }
        assert after == before


class TestPloneVolto:
    def test_installed(self, portal, run_step, caplog, monkeypatch):
        monkeypatch.setattr(
            api.addon, "get_addon_ids", lambda limit="": ["plone.volto"]
        )
        with caplog.at_level(logging.WARNING):
            run_step(step.warn_without_plone_volto)
        assert "plone.volto" not in caplog.text

    def test_missing(self, portal, run_step, caplog, monkeypatch):
        monkeypatch.setattr(api.addon, "get_addon_ids", lambda limit="": [])
        with caplog.at_level(logging.WARNING):
            run_step(step.warn_without_plone_volto)
        assert "plone.volto is not installed" in caplog.text
