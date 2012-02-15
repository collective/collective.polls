# -*- coding:utf-8 -*-
from Acquisition import aq_parent


def anonymous_view_parent(obj):
    ''' Return if Anonymous has View permission on parent object '''
    parent = aq_parent(obj)
    roles = parent.rolesOfPermission('View')
    roles = [r['name'] for r in roles if r['selected']]
    return 'Anonymous' in roles
