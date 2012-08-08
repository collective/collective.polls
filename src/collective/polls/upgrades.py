# -*- coding: utf-8 -*-

import logging

from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from collective.polls.anon_behavior import IAnonymous

from collective.polls.config import PROJECTNAME


logger = logging.getLogger(PROJECTNAME)


def enableAnonymousBehavior(context):
    logger.info("Enable behavior for existing polls")
    portal = getSite()

    catalog = getToolByName(portal, "portal_catalog")

    results = catalog(portal_type="collective.polls.poll")

    logger.info("Need to upgrade %s poll(s)" % len(results))
    for brain in results:
        poll = brain.getObject()
        try:
            anon_b = IAnonymous(poll)
        except TypeError:
            # ok, the behavior is not enabled for polls, abort
            logger.info("The anonyous behavior is not enabled for 'poll' types. Aborting upgrade.")
            break

        # XXX: This doesn't work because 'allow_anonymous' got lost
        #      when removed from the base schema.
        allow_anon = getattr(poll, 'allow_anonymous', False)
        logger.info("Poll %s had its allow_anonynous as %s." % (poll.title, allow_anon))
        anon_b.allow_anonymous = allow_anon

    logger.info("Done.")