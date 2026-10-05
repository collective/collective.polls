# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 3.0.0a1 (2026-10-05)


### Breaking

- Changed the `options` field to a JSON field holding `{option_id, description}` objects. Option ids are now stable: they are kept when options are reordered, and new options get the next free id. A poll needs at least two options with distinct ids. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Changed who sees results: everyone once a poll is closed, reviewers always, and people who voted while it is open when the poll shows partial results. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Changed the Python API: anonymous voter ids are random strings, so `IPolls.anonymous_vote_id()` returns a `str`; `Poll.voters()` is sorted; `Poll.setVote(option, request=None)` takes `option`, does not count `True` or `False` as an option, and raises `AlreadyVoted`, a subclass of `Unauthorized`, for a second vote. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Moved votes to a new storage on each poll. Run the upgrade step to profile version 3000 after updating: it moves the votes of every poll, removes vote portlet assignments, lets anonymous visitors vote again in open polls whose permission was reset, and removes the 2.x tile and resource registrations. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Supported Plone 6.2 only, on Python 3.10 to 3.14. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Removed the Classic UI: the poll views, the vote portlet, the collective.cover tile, the options widget and the JavaScript and CSS resources. Polls are shown and voted on in Volto, with the `@plone-collective/volto-polls` add-on. @ericof [#139](https://github.com/collective/collective.polls/issues/139)


### Feature

- Completed the Brazilian Portuguese translation. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added the `@poll` and `@vote` REST API services: read the state and results of a poll, and vote in it. Anonymous answers of `@poll` can be cached by a proxy. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Made the poll a container that holds images, and enabled the preview image link behavior on it. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added multiple choice polls: the new "Number of options a user can pick" field lets a voter pick from 1 to that many options, sent to `@vote` as `option_ids`. Results of a multiple choice poll are shares of voters. A new "Legend" field sets the text above the options. The poll form groups its fields in the Voting and Results fieldsets. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added the "Shuffle options" field, so a poll can show its options in random order. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Exported the votes of closed polls with plone.exportimport, and imported them back, so a site keeps its poll results across an export and import. The votes are only written during an import, never through the REST API. @ericof [#139](https://github.com/collective/collective.polls/issues/139)


### Bugfix

- Fixed duplicate-vote protection for anonymous visitors: their cookie had a fixed expiry date in 2020. It now lasts one year, with `SameSite=Lax`, and is `Secure` on HTTPS. @ericof [#139](https://github.com/collective/collective.polls/issues/139)


### Internal

- Rebuilt the package on the cookieplone monorepo add-on template: hatchling, a native namespace package, type hints checked with mypy, and a pytest suite with full branch coverage. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
