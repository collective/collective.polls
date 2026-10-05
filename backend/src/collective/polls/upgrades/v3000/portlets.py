"""Remove the 2.x vote portlet: its type and every assignment of it."""

from collections.abc import Iterator
from collective.polls import logger
from itertools import chain
from plone import api
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.tool import SetupTool
from typing import Any
from zope.annotation.interfaces import IAnnotations
from zope.component import getSiteManager
from zope.component import getUtilitiesFor

import transaction


#: Name the 2.x portlet type was registered under.
PORTLET_TYPE = "collective.polls.VotePortlet"

#: Module of the 2.x assignment class. Matching on it also catches
#: assignments that load as broken objects.
ASSIGNMENT_MODULE = "collective.polls.portlet.voteportlet"

#: Objects visited between savepoints.
BATCH_SIZE = 1000


def is_vote_assignment(assignment: Any) -> bool:
    """Tell whether a portlet assignment is a 2.x vote portlet.

    :param assignment: A stored assignment.
    :returns: ``True`` for the 2.x vote portlet, broken or not.
    """
    return type(assignment).__module__ == ASSIGNMENT_MODULE


def clean_mapping(mapping: Any) -> int:
    """Delete the vote portlets from one assignment mapping.

    :param mapping: A portlet assignment mapping.
    :returns: How many assignments were deleted.
    """
    keys = [key for key, value in mapping.items() if is_vote_assignment(value)]
    for key in keys:
        del mapping[key]
    return len(keys)


def context_mappings() -> Iterator[Any]:
    """Yield the portlet assignment mappings stored on content.

    The site root and every catalogued object, read from their annotations
    so that objects without portlets are not written to.

    :returns: An iterator over the mappings.
    """
    portal = api.portal.get()
    # plone-stubs declares the catalog's search methods as returning None.
    catalog: Any = api.portal.get_tool("portal_catalog")
    # An empty catalog query matches nothing; the site path matches all.
    path = "/".join(portal.getPhysicalPath())
    brains = catalog.unrestrictedSearchResults(path=path)
    objects = chain([portal], (brain._unrestrictedGetObject() for brain in brains))
    for index, obj in enumerate(objects, start=1):
        stored = IAnnotations(obj).get(CONTEXT_ASSIGNMENT_KEY)
        if stored:
            yield from stored.values()
        if index % BATCH_SIZE == 0:
            transaction.savepoint(optimistic=True)


def category_mappings() -> Iterator[Any]:
    """Yield the assignment mappings of every manager's user, group and type.

    The user category holds the dashboards.

    :returns: An iterator over the mappings.
    """
    for _name, manager in getUtilitiesFor(IPortletManager):
        for category in (USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY):
            mappings = manager.get(category)
            if mappings:
                yield from mappings.values()


def remove_vote_portlets(setup_tool: SetupTool) -> None:
    """Delete every vote portlet assignment and unregister the portlet type.

    :param setup_tool: The ``portal_setup`` tool.
    """
    removed = 0
    for mapping in chain(context_mappings(), category_mappings()):
        removed += clean_mapping(mapping)
    sm: Any = getSiteManager(api.portal.get())
    unregistered = sm.unregisterUtility(provided=IPortletType, name=PORTLET_TYPE)
    logger.info(
        "Portlets: %d vote portlet assignments removed, portlet type %s",
        removed,
        "unregistered" if unregistered else "was not registered",
    )
