from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


# plone.restapi reads each method of these utilities with getattr and skips
# the ones a utility does not define, so one method is a complete utility.
@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self) -> set[str]:
        return {"image_field", "image_scales", "effective", "Subject"}
