# -*- coding:utf-8 -*-

from five import grok
from zope.interface import Interface

from collective.polls import MessageFactory as _


class LegendOthersTranslation(grok.View):

    grok.context(Interface)
    grok.name('legendothers_translation.js')
    grok.require('zope2.View')

    def render(self):
        response = self.request.response
        response.setHeader('content-type', 'text/javascript;;charset=utf-8')

        label_legendothers = _(u"label_legendothers", default=u"Others")
        return "legendothers_translation = '%s';" % label_legendothers
