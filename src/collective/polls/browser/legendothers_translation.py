from five import grok
from zope.interface import Interface


class LegendOthersTranslation(grok.View):

    grok.context(Interface)
    grok.name('legendothers_translation.js')
    grok.require('zope2.View')
