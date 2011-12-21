# -*- coding:utf-8 -*-
from five import grok

from zope import schema

from zope.annotation.interfaces import IAnnotations

from plone.directives import dexterity
from plone.directives import form

from collective.polls import MessageFactory as _

class IPoll(form.Schema):
    """
    A poll
    """

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


class Poll(dexterity.Item):

    grok.implements(IPoll)

    def getAnswers(self):
        return self.answers

    def getResults(self):
        annotations = IAnnotations(self)
        all_votes = []
        for (index, answer) in enumerate(self.getAnswers()):
            votes = annotations.get("answer.%s"%index, 0)
            all_votes.append((answer, votes))
        return all_votes


class PollEditForm(dexterity.EditForm):

    grok.context(IPoll)

    def render(self):
        return super(PollEditForm, self).render()


class View(grok.View):

    grok.context(IPoll)
    grok.require('zope2.View')

    grok.name('view')

    def getAnswers(self):
        return self.context.getAnswers()

    def getResults(self):
        return self.context.getResults()
