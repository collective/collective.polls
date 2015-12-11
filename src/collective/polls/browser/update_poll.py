# -*- coding: utf-8 -*-
from collective.polls.browser import PollsViewMixin
from Products.Five.browser import BrowserView


class UpdatePollView(PollsViewMixin, BrowserView):

    """View to update poll results"""

    def poll(self):
        return self.context

    def __call__(self):
        # avoid issues with reverse proxies:
        # define response as non-cacheable and require revalidation
        self.request.response.setHeader('Cache-Control', 'no-cache, must-revalidate')
        return super(UpdatePollView, self).__call__()
