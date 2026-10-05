"""Remove what 2.x registered for Classic UI, and check for Volto support."""

from collective.polls import logger
from plone import api
from plone.registry.interfaces import IRegistry
from Products.GenericSetup.tool import SetupTool
from zope.component import getUtility


#: The name 2.x registered its tile under.
TILE_NAME = "collective.polls"

#: Registry records listing tiles, one per tile framework.
TILE_RECORDS = (
    "plone.app.tiles",
    "collective.cover.controlpanel.ICoverSettings.available_tiles",
)

#: How 2.x static resources are addressed.
RESOURCE_MARKER = "++resource++collective.polls"


def _remove_tile(registry: IRegistry, name: str) -> bool:
    """Take the 2.x tile out of one registry record listing tiles.

    :param registry: The site registry.
    :param name: The record name.
    :returns: ``True`` when the record listed the tile.
    """
    record = registry.records.get(name)
    if record is None or TILE_NAME not in (record.value or []):
        return False
    record.value = [tile for tile in record.value if tile != TILE_NAME]
    return True


def _remove_resources(registry: IRegistry) -> int:
    """Remove registry records pointing at 2.x static resources.

    A record whose text value mentions them is deleted; a list value only
    loses the entries that do. Record names cannot hold ``+``, so a name
    never mentions them.

    :param registry: The site registry.
    :returns: How many records were deleted or changed.
    """
    changed = 0
    for name in list(registry.records.keys()):
        value = registry.records[name].value
        if isinstance(value, str) and RESOURCE_MARKER in value:
            del registry.records[name]
            changed += 1
        elif isinstance(value, (list, tuple)) and any(
            isinstance(item, str) and RESOURCE_MARKER in item for item in value
        ):
            kept = [
                i for i in value if not (isinstance(i, str) and RESOURCE_MARKER in i)
            ]
            registry.records[name].value = type(value)(kept)
            changed += 1
    return changed


def remove_legacy_registrations(setup_tool: SetupTool) -> None:
    """Remove the 2.x tile and static resources from the registry.

    :param setup_tool: The ``portal_setup`` tool.
    """
    registry = getUtility(IRegistry)
    tiles = [name for name in TILE_RECORDS if _remove_tile(registry, name)]
    resources = _remove_resources(registry)
    logger.info(
        "Registry: tile removed from %s; %d resource records cleaned",
        tiles or "no record",
        resources,
    )


def warn_without_plone_volto(setup_tool: SetupTool) -> None:
    """Warn when the site cannot show polls: 3.0 is for Volto sites only.

    Installing ``plone.volto`` changes much more than polls, so the upgrade
    leaves that decision to the site's administrator.

    :param setup_tool: The ``portal_setup`` tool.
    """
    if "plone.volto" not in api.addon.get_addon_ids(limit="installed"):
        logger.warning(
            "plone.volto is not installed: collective.polls 3.0 has no "
            "Classic UI, so polls cannot be shown or voted on in this site."
        )
