"""The 2.x vote portlet assignment, kept only so stored ones can be loaded.

Version 3.0 has no portlet: the poll block replaces it. Sites upgraded from
2.x may still hold assignments of this class in their portlet managers;
without the class they would load as broken objects. The upgrade to 3000
deletes them. Nothing registers this as a portlet, and no code here renders
or edits it.

Deprecated: removed in 4.0.
"""

from plone.app.portlets.portlets import base


class Assignment(base.Assignment):
    """A stored 2.x vote portlet assignment. Deprecated."""

    poll = "latest"
    header = ""
    show_total = True
    show_closed = False
    link_poll = True

    @property
    def title(self) -> str:
        """Return the title shown for the assignment."""
        return "Voting portlet (removed)"
