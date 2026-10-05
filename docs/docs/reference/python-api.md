---
myst:
  html_meta:
    "description": "The Python API of collective.polls: the IPolls utility, the IPollVotes adapter, and the Poll class."
    "property=og:description": "The Python API of collective.polls: the IPolls utility, the IPollVotes adapter, and the Poll class."
    "property=og:title": "Python API"
    "keywords": "Plone, polls, Python API, IPolls, IPollVotes"
---

# Python API

## The `IPolls` utility

A named utility, `collective.polls`, to find polls and ask permission questions about them.

```python
from collective.polls.utility import IPolls
from zope.component import getUtility

polls = getUtility(IPolls, name="collective.polls")
```

| Method | Returns |
|---|---|
| `recent_polls(context=None, show_all=False, limit=5, **kw)` | Catalog brains of the newest polls, below `context` when given. Only open polls unless `show_all` is true. |
| `poll_by_uid(uid, context=None)` | The poll with that UID, or the latest open poll below `context` when `uid` is `"latest"`; `None` when there is none. |
| `voted_in_a_poll(poll, request=None)` | Whether the current user voted. Anonymous users are recognized by their cookie, so they need the request. |
| `allowed_to_edit(poll)` | Whether the current user holds `Modify portal content` on the poll. |
| `allowed_to_view(poll)` | Whether the current user holds `View` on the poll. |
| `allowed_to_vote(poll, request=None)` | `True` when the current user may vote. Raises `Unauthorized` without the vote permission, and `AlreadyVoted` after a vote. |
| `anonymous_vote_id()` | A new random id for an anonymous vote. |

## The `IPollVotes` adapter

Adapt a poll to read or change its votes.
Reading never writes to the database.

```python
from collective.polls.interfaces import IPollVotes

votes = IPollVotes(poll)
votes.counts()  # {0: 2, 1: 1}
```

| Method | Description |
|---|---|
| `counts()` | Votes per option id, for every current option, zero included. |
| `orphans()` | Votes recorded for option ids the poll no longer has. |
| `total()` | Number of votes for the current options. |
| `voters()` | Ids of everyone who voted, sorted. Anonymous voters are `Anonymous-` followed by a random id. |
| `has_voter(voter_id)` | Whether a voter id already voted. |
| `voter_count()` | Number of people who voted. |
| `register(option_id, voter_id)` | Records one voter's vote, for one option id or a list of them. Raises `ValueError` for an unknown or repeated id, and `AlreadyVoted` for a voter who voted. |
| `clear()` | Removes the votes of the current options, and every voter. |
| `stored()` | Every vote recorded, for current and removed options, without zeros. |
| `replace(counts, voters)` | Drops every vote and stores these ones, without validating them. |
| `merge(counts, voters)` | Adds votes in bulk to what is stored, without validating them. |

`register` checks only the ids and the voter.
To vote as the current user, with the permission checks and the anonymous cookie, call `Poll.setVote` instead.

## The `Poll` class

| Member | Description |
|---|---|
| `getOptions()` | The options, as `{"option_id", "description"}` dictionaries. |
| `getResults()` | `(description, votes, fraction)` for each option, or an empty list before the first vote. |
| `setVote(option, request=None)` | Votes as the current user, for one option id or a list of them. Returns `False` for an invalid choice. Raises `Unauthorized` or `AlreadyVoted`, like `IPolls.allowed_to_vote`. |
| `voters()` | Same as `IPollVotes.voters()`. |
| `multiple_choice` | Whether a voter can pick more than one option. |
| `total_votes` | Votes so far: one per voter. |

## Exceptions

| Exception | Module | Raised |
|---|---|---|
| `AlreadyVoted` | `collective.polls.interfaces` | For a second vote by the same voter. A subclass of `AccessControl.Unauthorized`. |
