# -*- coding: utf-8 -*-
from collective.polls.logger import logger
from plone import api


def issue_83(context):
    """Remove missing view from JS registry."""
    js_tool = api.portal.get_tool('portal_javascripts')
    id = '@@legendothers_translation.js'
    if id in js_tool.getResourceIds():
        js_tool.unregisterResource(id)
        logger.info('"{0}" resource was removed'.format(id))
        js_tool.cookResources()
        logger.info('JS resources were cooked')
