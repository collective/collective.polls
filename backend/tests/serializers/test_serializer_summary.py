"""Metadata the summary serializer adds to every listing."""

from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.component import getUtility


def test_default_metadata_fields(portal):
    utility = getUtility(
        IJSONSummarySerializerMetadata,
        name="collective.polls.summary_serializer_metadata",
    )
    assert utility.default_metadata_fields() == {
        "image_field",
        "image_scales",
        "effective",
        "Subject",
    }
