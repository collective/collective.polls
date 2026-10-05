"""A closed poll's votes, carried through plone.exportimport.

Both adapters are registered for plone.exportimport's request marker, which
the request provides only while plone.exportimport exports or imports
content. A REST API call never gets them: its ``GET`` does not show the
votes, and its ``PATCH`` or ``POST`` cannot write them.

Only a closed poll's votes are exported, as::

    "collective.polls.votes": {
        "counts": {"0": 2, "1": 1},
        "voters": ["Anonymous-…", "member-id"]
    }

Counts keep votes for removed options, so nothing recorded is lost.
"""

from collections.abc import Iterable
from collective.polls.config import EXPORT_VOTES_KEY
from collective.polls.config import EXPORT_VOTES_STATE
from collective.polls.content.poll import IPoll
from collective.polls.interfaces import IPollVotes
from plone import api
from plone.exportimport.interfaces import IExportImportRequestMarker
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from typing import Any
from typing import TypedDict
from zope.component import adapter
from zope.interface import implementer


class ExportedVotesDict(TypedDict):
    """A poll's votes, as an export holds them."""

    counts: dict[str, int]
    voters: list[str]


def export_votes(poll: IPoll) -> ExportedVotesDict:
    """Return a poll's votes in a form JSON can hold.

    :param poll: The poll.
    :returns: Counts keyed by the option id as a string, and the voters.
    """
    votes = IPollVotes(poll)
    return {
        "counts": {str(option_id): n for option_id, n in votes.stored().items()},
        "voters": votes.voters(),
    }


def import_votes(poll: IPoll, value: dict[str, Any]) -> None:
    """Replace a poll's votes with exported ones.

    :param poll: The poll.
    :param value: What :func:`export_votes` returned, read back from JSON.
    :raises ValueError: When a count or option id is not an integer.
    """
    counts = {int(key): int(n) for key, n in (value.get("counts") or {}).items()}
    voters: Iterable[str] = (str(voter) for voter in value.get("voters") or [])
    IPollVotes(poll).replace(counts, voters)


@implementer(ISerializeToJson)
@adapter(IPoll, IExportImportRequestMarker)
class ExportPollSerializer(SerializeFolderToJson):
    """Serialize a poll for plone.exportimport, with its votes once closed."""

    def __call__(
        self,
        version: str | None = None,
        include_items: bool = True,
        include_expansion: bool = True,
    ) -> dict[str, Any]:
        result = super().__call__(
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )
        if api.content.get_state(self.context) == EXPORT_VOTES_STATE:
            result[EXPORT_VOTES_KEY] = export_votes(self.context)
        return result


@implementer(IDeserializeFromJson)
@adapter(IPoll, IExportImportRequestMarker)
class ImportPollDeserializer(DeserializeFromJson):
    """Deserialize a poll for plone.exportimport, writing exported votes.

    The votes are written after the fields, so they are counted against the
    imported options. plone.exportimport sets the workflow state afterwards,
    by transitions that never clear votes.
    """

    def __call__(
        self,
        validate_all: bool = False,
        data: dict[str, Any] | None = None,
        create: bool = False,
        mask_validation_errors: bool = True,
    ) -> IPoll:
        if data is None:
            data = json_body(self.request)
        context = super().__call__(
            validate_all=validate_all,
            data=data,
            create=create,
            mask_validation_errors=mask_validation_errors,
        )
        value = data.get(EXPORT_VOTES_KEY)
        if value:
            import_votes(self.context, value)
        return context
