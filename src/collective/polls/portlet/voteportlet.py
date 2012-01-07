# -*- coding:utf-8 -*-
from AccessControl import Unauthorized

from zope import schema
from zope.formlib import form

from zope.component import queryUtility

from zope.interface import implements
from zope.interface import alsoProvides

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.memoize.instance import memoize

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.polls.polls import IPolls

from collective.polls import MessageFactory as _


def PossiblePolls(context):
    catalog = getToolByName(context, 'portal_catalog')
    polls = catalog(portal_type="collective.polls.poll", review_state="open")

    values = [SimpleTerm(value="latest", title=_(u"Latest open poll"))]
    if polls:
        for i in polls:
            values.append(SimpleTerm(value=i.UID, title=i.Title))

    vocab = SimpleVocabulary(values)

    return vocab


alsoProvides(PossiblePolls, IContextSourceBinder)


class IVotePortlet(IPortletDataProvider):
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                             description=_(u'''The header for the portlet.
                                               Leave empty for none.'''),
                             required=False)

    poll = schema.Choice(title=_(u'Poll'),
                         description=_(u"Which poll to show in the portlet."),
                         required=True,
                         source=PossiblePolls)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IVotePortlet)

    header = u""
    poll = None

    def __init__(self, poll, header = u""):
        self.header = header
        self.poll = poll

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Voting portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('voteportlet.pt')

    @property
    def utility(self):
        ''' Access to IPolls utility '''
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    @memoize
    def poll(self):
        utility = self.utility
        uid = self.data.poll
        poll = utility.poll_by_uid(uid)
        return poll

    def poll_uid(self):
        ''' Return uid for current poll '''
        utility = self.utility
        return utility.uid_for_poll(self.poll())

    def getVotingResults(self):
        poll = self.poll()
        if poll.show_results:
            return poll.getResults()
        else:
            return None

    @property
    def can_vote(self):
        utility = self.utility
        poll = self.poll()
        try:
            return utility.allowed_to_vote(poll, self.request)
        except Unauthorized:
            return False

    @property
    def available(self):
        utility = self.utility
        poll = self.poll()
        if poll:
            can_view = utility.allowed_to_view(poll)
            # Do not show this portlet in the poll context
            return can_view and not (poll == self.context)
        return False


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IVotePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IVotePortlet)
