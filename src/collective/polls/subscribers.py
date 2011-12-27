# -*- coding:utf-8 -*-
from five import grok

from Products.CMFCore.interfaces import IActionSucceededEvent

from collective.polls.content.poll import IPoll

from collective.polls.config import PERMISSION_VOTE

ALL_ROLES = ['Anonymous', 'Contributor', 'Editor', 'Manager', 'Member',
             'Reader', 'Reviewer', 'Site Administrator']


@grok.subscribe(IPoll, IActionSucceededEvent)
def fix_permissions(poll, event):
    ''' This subscriber will fix permission on poll object if
        allow_anonymous is enabled
    '''
    if event.action in ['publish', ]:
        # Poll has been opened
        allow_anonymous = poll.allow_anonymous
        if allow_anonymous:
            poll.manage_permission(PERMISSION_VOTE,
                                   ALL_ROLES,
                                   acquire=0)
