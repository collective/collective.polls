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
