# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from five import grok

from zope import schema
from zope import interface

from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter

from z3c.form.interfaces import HIDDEN_MODE

from plone.directives import dexterity
from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from collective.polls.config import VOTE_ANNO_KEY

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

    options = schema.List(
        title = _(u"Available Options"),
        value_type = DictRow(title=_(u'Option'),
                             schema=IOption),
        default=[],
        required=True)


class Poll(dexterity.Item):
    """ A Poll in a Plone site
    """

    grok.implements(IPoll)

    def getOptions(self):
        ''' Returns available options '''
        options = self.options
        return options

    def getResults(self):
        ''' Returns results so far '''
        annotations = IAnnotations(self)
        all_votes = []
        for option in self.getOptions():
            index = option.get('option_id')
            description = option.get('description')
            votes = annotations.get(VOTE_ANNO_KEY % index, 0)
            all_votes.append((description, votes))
        return all_votes


class PollAddForm(dexterity.AddForm):
    """ Form to handle creation of new Polls
    """

    grok.name('collective.polls.poll')

    def updateFields(self):
        ''' Update form fields to set options to use DataGridFieldFactory '''
        super(PollAddForm, self).updateFields()
        self.fields['options'].widgetFactory = DataGridFieldFactory

    def datagridUpdateWidgets(self, subform, widgets, widget):
        ''' Hides the widgets in the datagrid subform '''
        widgets['option_id'].mode = HIDDEN_MODE

    def updateWidgets(self):
        ''' Update form widgets to hide column option_id from end user '''
        super(PollAddForm, self).updateWidgets()
        self.widgets['options'].allow_reorder = True
        self.widgets['options'].columns[0]['mode']= HIDDEN_MODE

    def create(self, data):
        options = data['options']
        for (index, option) in enumerate(options):
            option['option_id'] = index
        return super(PollAddForm, self).create(data)


class PollEditForm(dexterity.EditForm):
    """ Form to handle edition of existing Polls
    """

    grok.context(IPoll)

    def updateFields(self):
        ''' Update form fields to set options to use DataGridFieldFactory '''
        super(PollEditForm, self).updateFields()
        self.fields['options'].widgetFactory = DataGridFieldFactory

    def datagridUpdateWidgets(self, subform, widgets, widget):
        ''' Hides the widgets in the datagrid subform '''
        widgets['option_id'].mode = HIDDEN_MODE

    def updateWidgets(self):
        ''' Update form widgets to hide column option_id from end user '''
        super(PollEditForm, self).updateWidgets()
        self.widgets['options'].allow_reorder = True
        self.widgets['options'].columns[0]['mode']= HIDDEN_MODE

    def applyChanges(self, data):
        options = data['options']
        for (index, option) in enumerate(options):
            option['option_id'] = index
        super(PollEditForm, self).applyChanges(data)


class View(grok.View):

    grok.context(IPoll)
    grok.require('zope2.View')

    grok.name('view')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.wf_state = self.state.workflow_state()

    def getOptions(self):
        ''' Returns available options '''
        return self.context.getOptions()

    def getResults(self):
        ''' Returns results so far if allowed'''
        show_results = False
        if self.wf_state == 'open':
            show_results = show_results or self.context.show_results
        elif self.wf_state == 'closed':
            show_results = True
        return (show_results and self.context.getResults()) or None
