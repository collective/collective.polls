# -*- coding: utf-8 -*-
from collective.polls.logger import logger
from plone import api


def cook_css_resources(context):
    """Cook css resources."""
    css_tool = api.portal.get_tool('portal_css')
    css_tool.cookResources()
    logger.info('CSS resources were cooked')


def cook_javascript_resources(context):
    """Cook javascript resources."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.cookResources()
    logger.info('Javascript resources were cooked')
