# -*- coding: utf-8 -*-
from collective.polls.logger import logger
from plone import api


def register_tasksplease_script(setup_tool):
    """Register script to remove dependency on collective.z3cform.widgets."""
    script = '++resource++collective.polls/js/jquery.tasksplease.js'
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.registerResource(script)
    assert script in js_tool.getResourceIds()
    logger.info('TasksPlease script registered')


def remove_excanvas_script(setup_tool):
    """Remove script used to add support for the canvas tag on IE8 and below."""
    script = '++resource++collective.polls/js/excanvas.min.js'
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.unregisterResource(script)
    assert script not in js_tool.getResourceIds()
    logger.info('ExplorerCanvas script removed')
