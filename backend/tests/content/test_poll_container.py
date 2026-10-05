"""A poll is a container that holds only images."""

from . import PORTAL_TYPE
from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import Container

import pytest


class TestPollContainer:
    @pytest.fixture(autouse=True)
    def _setup(self, portal) -> None:
        with api.env.adopt_roles(["Manager"]):
            self.poll = api.content.create(portal, PORTAL_TYPE, "poll")

    def test_is_container(self):
        assert isinstance(self.poll, Container)

    def test_allowed_types(self):
        allowed = [fti.getId() for fti in self.poll.allowedContentTypes()]
        assert allowed == ["Image"]

    def test_add_image(self):
        with api.env.adopt_roles(["Manager"]):
            image = api.content.create(self.poll, "Image", "image")
        assert image.portal_type == "Image"
        assert "image" in self.poll.objectIds()

    def test_add_document_refused(self):
        with api.env.adopt_roles(["Manager"]), pytest.raises(InvalidParameterError):
            api.content.create(self.poll, "Document", "document")
