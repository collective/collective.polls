from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.polls import MessageFactory as _

from zope.annotation.interfaces import IAnnotations

# Interface class; used to define content-type schema.

class IPoll(form.Schema):
    """
    A poll
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/poll.xml to define the content type
    # and add directives here as necessary.
    
    allow_anonymous = schema.Bool(
        title = _(u"Allow anonymous"),
        description = _(u"Allow not logged in users to vote."),
        )

    #multivalue = schema.Bool(
        #title = _(u"Multivalue"),
        #description = _(u"Voters can choose several answers at the same "
                         #"time."),
        #)

    show_results = schema.Bool(
        title = _(u"Show partial results"),
        description = _(u"Show partial results after a voter has already "
                         "voted."),
        )

    answers = schema.List(
        title = _(u"Answers"),
        value_type = schema.Text(
                        title=_(u'Option'),
                        default=u''),
        default=[],
        required=False)
                            
# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Poll(dexterity.Item):
    grok.implements(IPoll)
    
    # Add your class methods and properties here

    def getAnswers(self):
        return self.answers

    def getResults(self):
        annotations = IAnnotations(self)
        all_votes = []
        for (index, answer) in enumerate(self.getAnswers()):
            votes = annotations.get("answer.%s"%index, 0)
            all_votes.append((answer, votes))
        return all_votes

# View class
# The view will automatically use a similarly named template in
# poll_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.


class PollEditForm(dexterity.EditForm):
    grok.context(IPoll)

    def render(self):
        return super(PollEditForm, self).render()


#class PollViewForm(dexterity.DisplayForm):
    #grok.context(IPoll)
    #grok.require('zope2.View')

    #def render(self):
        #return super(PollViewForm, self).render()
        
#class View(dexterity.DisplayForm):
    #grok.context(IPoll)
    #grok.require('zope2.View')
    
class View(grok.View):
    grok.context(IPoll)
    grok.require('zope2.View')
    
    grok.name('view')

    def getAnswers(self):
        return self.context.getAnswers()

    def getResults(self):
        return self.context.getResults()