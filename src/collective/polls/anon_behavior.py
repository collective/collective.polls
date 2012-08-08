from rwproperty import getproperty, setproperty

from zope import schema

from zope.component import adapts
from zope.interface import implements
from zope.interface import alsoProvides

from plone.directives import form

from collective.polls.content.poll import IPoll

from collective.polls import MessageFactory as _

class IAnonymous(form.Schema):
    """
    Add 'allow anonymous' field
    """
    
    form.order_before(allow_anonymous='show_results')
    allow_anonymous = schema.Bool(
        title=_(u"Allow anonymous"),
        description=_(u"Allow not logged in users to vote. The parent folder \
            of this poll should be published before opeining the poll for \
            this field to take effect"),
        default=True,
        )


alsoProvides(IAnonymous, form.IFormFieldProvider)


class Anonymous(object):
    """
    Stores and reads the 'allow_anonymous' value
    """
    implements(IAnonymous)
    adapts(IPoll)

    def __init__(self, context):
        self.context = context
    
    @getproperty
    def allow_anonymous(self):
        return getattr(self.context, 'allow_anonymous', False)

    @setproperty
    def allow_anonymous(self, value):
        setattr(self.context, 'allow_anonymous', value)