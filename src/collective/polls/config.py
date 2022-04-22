# -*- coding: utf-8 -*-
from plone import api


PROJECTNAME = 'collective.polls'
PROFILE = PROJECTNAME + ':default'

COOKIE_KEY = 'collective.poll.'
MEMBERS_ANNO_KEY = 'voters_members_id'
# FIXME: avoid module formatter, use {0:02d} instead of %02d
VOTE_ANNO_KEY = 'option.%02d'

PERMISSION_VOTE = 'collective.polls: Vote'

# Is this Plone 5 or higher?
IS_PLONE_5 = int(api.env.plone_version()[0]) >= 5
