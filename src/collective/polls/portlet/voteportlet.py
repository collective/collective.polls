# -*- coding:utf-8 -*-
from zope import schema
from zope.formlib import form

from zope.component import queryUtility

from zope.interface import implements
from zope.interface import alsoProvides

from zope.annotation.interfaces import IAnnotations

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.polls.config import MEMBERS_ANNO_KEY
from collective.polls.config import VOTE_ANNO_KEY

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

    def render(self):
        pt = ViewPageTemplateFile('voteportlet.pt')

        poll_submitted = 'poll.submit' in self.request.form

        if poll_submitted:
            # Let's recheck that the user hasn't already voted
            already_voted = self.hasAlreadyVoted()

            if not already_voted:
                # First we need to save the voted option
                answer = None
                for i in self.request.form:
                    if i.startswith('answer.'):
                        answer = self.request.form[i]

                if answer:
                    # If there's actually a proper answer
                    poll = self.getCurrentPoll()
                    answers = poll.getAnswers()
                    index = answers.index(answer.decode('utf-8'))

                    annotations = IAnnotations(poll)

                    votes = annotations.get(VOTE_ANNO_KEY % index, 0)
                    votes+=1
                    annotations["answer.%s"%index] = votes

                    # Now we need to mark the user so it cannot vote again
                    pm = getToolByName(self.context, 'portal_membership')
                    if not pm.isAnonymousUser():
                        member = pm.getAuthenticatedMember()
                        mem_ids = annotations.get(MEMBERS_ANNO_KEY,
                                                  [])
                        mem_ids.append(member.id)
                        annotations[MEMBERS_ANNO_KEY] = mem_ids

                    else:
                        # If he's anonymous, let's set a cookie
                        self.request.RESPONSE.setCookie('collective.poll',
                                                        IUUID(poll))

                # If the poll was submitted, let's redirect to make the changes
                # visible
                self.request.RESPONSE.redirect(self.context.absolute_url())

        return pt(self)

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    @memoize
    def getCurrentPoll(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        uid = self.data.poll
        if uid == 'latest':
            # We should get the latest open poll to use in the portlet
            poll = catalog(portal_type="collective.polls.poll",
                           review_state="open",
                           sort_on="created",
                           sort_order="reverse")
        else:
            poll = catalog(UID=uid)

        if poll:
            return poll[0].getObject()
        else:
            return None

    def hasAlreadyVoted(self):
        voted = False
        pm = getToolByName(self.context, 'portal_membership')
        poll = self.getCurrentPoll()
        if poll:
            annotations = IAnnotations(poll)
            if not pm.isAnonymousUser():
                member = pm.getAuthenticatedMember()
                mem_ids = annotations.get(MEMBERS_ANNO_KEY, [])
                if member.id in mem_ids:
                    voted = True
            else:
                poll_uid = self.request.cookies.get('collective.poll')
                if poll_uid and IUUID(poll) == poll_uid:
                    voted = True

        return voted

    def getVotingResults(self):
        poll = self.getCurrentPoll()
        if poll.show_results:
            return poll.getResults()
        else:
            return None

    @property
    def available(self):
        view = True
        # Check if the poll accept anonymous voting, if not, do not show
        # the portlet
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser() and not self.getCurrentPoll().allow_anonymous:
            view = False

        # If we have already voted and we we should not see partial results
        # do not show the portlet either
        if self.hasAlreadyVoted() and not self.getVotingResults():
            view = False
        return view


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
