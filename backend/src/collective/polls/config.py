"""Constants shared across the package."""

#: Portal type id of a poll.
PORTAL_TYPE = "collective.polls.poll"

#: Workflow bound to polls.
WORKFLOW_ID = "poll_workflow"

#: Permission to vote in a poll.
PERMISSION_VOTE = "collective.polls: Vote"

#: Name of the cookie set for an anonymous voter, followed by the poll's UID.
COOKIE_KEY = "collective.poll."

#: How long the anonymous voting cookie lasts, in seconds.
COOKIE_MAX_AGE = 60 * 60 * 24 * 365

#: Prefix of the voter id recorded for an anonymous vote.
ANONYMOUS_PREFIX = "Anonymous-"

#: Annotation key holding the votes of a poll.
VOTES_ANNO_KEY = "collective.polls.votes"

#: Key holding a closed poll's votes in a plone.exportimport export.
EXPORT_VOTES_KEY = "collective.polls.votes"

#: Review state whose votes plone.exportimport exports.
EXPORT_VOTES_STATE = "closed"
