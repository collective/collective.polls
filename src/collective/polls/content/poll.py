# -*- coding:utf-8 -*-
from five import grok

from zope import schema
from zope import interface

from zope.annotation.interfaces import IAnnotations

from plone.directives import dexterity
from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from collective.polls import MessageFactory as _


class IOption(interface.Interface):
    ''' An option in a poll '''

    option_id = schema.Int(title=u"Option Id",
                           required=False)

    description = schema.TextLine(title=_(u"Description"),
                                  required=True)


class IPoll(form.Schema):
    """ A Poll in a Plone site
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
        value_type = DictRow(title=_(u'Option'),
                             schema=IOption),
        default=[],
        required=True)


class Poll(dexterity.Item):
    """ A Poll in a Plone site
    """

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
