# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.polls import MessageFactory as _
from collective.polls.polls import IPolls
from plone import api
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletRetriever
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class PollsViewMixin:

    """Common methods and functions used by views, tiles and portlets."""

    @property
    def utility(self):
        """Access to IPolls utility."""
        utility = queryUtility(IPolls, name='collective.polls')
        return utility

    @property
    def available(self):
        """Check if Poll is available."""
        utility = self.utility
        poll = self.poll()
        if poll:
            can_view = utility.allowed_to_view(poll)
            # Do not show this portlet in the poll context
            return can_view and not (poll == self.context)
        return False

    def poll_uid(self):
        """Return UUID for current poll."""
        return api.content.get_uuid(self.poll())

    @property
    def can_vote(self):
        """Check if user can vote."""
        if getattr(self, '_has_voted', False) and self._has_voted:
            # This is mainly to avoid anonymous users seeing the form again
            return False
        utility = self.utility
        poll = self.poll()
        if poll:
            try:
                return utility.allowed_to_vote(poll, self.request)
            except Unauthorized:
                return False
        return False

    @property
    def can_edit(self):
        """Check if user can edit the poll."""
        utility = self.utility
        poll = self.poll()
        return utility.allowed_to_edit(poll)

    def is_closed(self):
        """Check if poll is closed."""
        state = 'closed'
        poll = self.poll()
        if poll:
            state = poll.portal_workflow.getInfoFor(
                poll, 'review_state')
        return state == 'closed'

    @property
    def has_voted(self):
        """Return True if the current user voted in this poll."""
        if getattr(self, '_has_voted', False) and self._has_voted:
            return True
        poll = self.poll()
        utility = self.utility
        voted = utility.voted_in_a_poll(poll, self.request)
        return voted

    def voting_results(self):
        """Get the voting results."""
        poll = self.poll()
        if poll and poll.show_results:
            return poll.getResults()
        return None

    @property
    def total_votes(self):
        """Return the number of votes so far."""
        poll = self.poll()
        return poll.total_votes


class View(PollsViewMixin, BrowserView):

    index = ViewPageTemplateFile('templates/view.pt')

    def render(self):
        return self.index()

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        context = aq_inner(self.context)
        self.context = context
        self.state = getMultiAdapter(
            (context, self.request), name=u'plone_context_state')
        self.wf_state = self.state.workflow_state()
        # Handle vote
        form = self.request.form
        self.errors = []
        self.messages = []

        # if the poll is open and anonymous should vote but the parent folder
        # is private.. inform the user.

        # When the poll's container is the site's root, we do not need to
        # check the permissions.
        container = aq_parent(aq_inner(self.context))

        if 'open' == self.wf_state and not ISiteRoot.providedBy(container):
            roles = [
                r['name'] for r in
                self.context.rolesOfPermission('collective.polls: Vote')
                if r['selected']]

            if 'Anonymous' not in roles and self.context.allow_anonymous:
                msg = _(
                    u"Anonymous user won't be able to vote, you forgot to "
                    u'publish the parent folder, you must sent back the poll '
                    u'to private state, publish the parent folder and open '
                    u'the poll again')
                api.portal.show_message(msg, self.request, type='warn')

        if 'poll.submit' in form:
            self._updateForm(form)
        # Update status messages
        for error in self.errors:
            api.portal.show_message(error, self.request, type='warn')
        for msg in self.messages:
            api.portal.show_message(msg, self.request, type='info')

        # XXX
        # if 'voting.from' in form:
        #     url = form['voting.from']
        #     self.request.RESPONSE.redirect(url)

    def _updateForm(self, form):
        INVALID_OPTION = _(u'Invalid option')
        options = form.get('options', '')
        if isinstance(options, list):
            self.errors.append(INVALID_OPTION)
        elif isinstance(options, str):
            if not options.isdigit():
                self.errors.append(INVALID_OPTION)
            else:
                options = int(options)
        if not self.errors:
            # Let's vote
            try:
                self.context.setVote(options, self.request)
                self.messages.append(_(u'Thanks for your vote'))
                # We do this to avoid redirecting anonymous user as
                # we just sent them the cookie
                self._has_voted = True
            except Unauthorized:
                self.errors.append(_(u'You are not authorized to vote'))

    def poll(self):
        return self.context

    def getOptions(self):
        """Return available options."""
        return self.context.getOptions()


class PollPortletRender(BrowserView):

    """This methods allow to use the portlet render in a view."""

    def get_portlet_manager(self, column=''):
        """Return one of default Plone portlet managers.

        @param column: "plone.leftcolumn" or "plone.rightcolumn"

        @return: plone.portlets.interfaces.IPortletManagerRenderer instance
        """
        if column:
            try:
                manager = getUtility(IPortletManager, name=column)
            except ComponentLookupError:
                # Happens when using polls in a panel from collective.panels
                manager = None
        else:
            manager = getUtility(IPortletManager, name='plone.rightcolumn')
            if not manager:
                manager = getUtility(IPortletManager, name='plone.leftcolumn')
        return manager

    def render_portlet(self, context, request, view, manager, interface):
        """Render a portlet defined in external location.

        .. note ::

            Portlets can be idenfied by id (not user visible)
            or interface (portlet class). This method supports look up
            by interface and will return the first matching portlet with
            this interface.

        @param context: Content item reference where portlet appear

        @param manager: IPortletManagerRenderer instance

        @param view: Current view or None if not available

        @param interface: Marker interface class we use to identify
            the portlet. E.g. IFacebookPortlet

        @return: Rendered portlet HTML as a string, or empty string if
            portlet not found
        """
        if manager is None:
            return ''

        retriever = getMultiAdapter((context, manager), IPortletRetriever)

        portlets = retriever.getPortlets()

        assignment = None

        for portlet in portlets:

            # portlet is {'category': 'context',
            # 'assignment': <FacebookLikeBoxAssignment at facebook-like-box>,
            # 'name': u'facebook-like-box',
            # 'key': '/isleofback/sisalto/huvit-ja-harrasteet
            # Identify portlet by interface provided by assignment
            if interface.providedBy(portlet['assignment']):
                assignment = portlet['assignment']
                break

        if assignment is None:
            # Did not find a portlet
            return ''

        # - A special type of content provider, IPortletRenderer, knows how to
        # render each type of portlet. The IPortletRenderer should be a
        # multi-adapter from (context, request, view, portlet manager,
        #                     data provider).

        renderer = queryMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer)

        # Make sure we have working acquisition chain
        renderer = renderer.__of__(context)

        if renderer is None:
            raise RuntimeError(
                'No portlet renderer found for portlet assignment: ' + str(assignment))

        renderer.update()
        # Does not check visibility here... force render always
        html = renderer.render()

        return html

    def render(self):
        """Render a portlet from another page in-line to this page.

        Does not render other portlets in the same portlet manager.
        """
        context = self.context.aq_inner
        request = self.request
        view = self

        # Alternatively, you can directly query your custom portlet manager
        # by interface
        from collective.polls.portlet.voteportlet import IVotePortlet
        column = self.request['column'] if 'column' in self.request else ''
        manager = self.get_portlet_manager(column)

        html = self.render_portlet(context, request, view,
                                   manager, IVotePortlet)
        return html
