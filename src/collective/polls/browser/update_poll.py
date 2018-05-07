# -*- coding: utf-8 -*-
from collective.polls.browser import PollsViewMixin
from Products.Five.browser import BrowserView


class UpdatePollView(PollsViewMixin, BrowserView):
    """View to show poll results."""

    def poll(self):
        return self.context

    def is_safe_method(self):
        """Check if the request was made using a safe method."""
        safe_methods = ('GET', 'HEAD')
        return self.request.get('REQUEST_METHOD', 'GET').upper() in safe_methods

    def __call__(self):
        """Render the results of a poll.

        Make use of HTTP caching headers to decrease server usage:
        results are not cached on browsers and are cached 120 seconds
        on intermediate caches. We use the last modified date as ETag
        to return a 304 (Not Modified) status in case the poll has not
        being modified since last time it was accessed.

        More information: https://httpwg.org/specs/rfc7234.html
        """
        if not self.is_safe_method():
            self.request.response.setStatus(412)  # Precondition Failed
            return ''

        modified = str(self.context.modified().timeTime())
        self.request.response.setHeader('Cache-Control', 'max-age=0, s-maxage=120')
        self.request.response.setHeader('ETag', modified)

        match = self.request.get_header('If-None-Match', '')
        if modified == match:
            self.request.response.setStatus(304)  # Not Modified
            return ''

        return super(UpdatePollView, self).__call__()
