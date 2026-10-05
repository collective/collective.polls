---
myst:
  html_meta:
    "description": "Where collective.polls stores votes, why the REST API cannot change them, and how they survive an export."
    "property=og:description": "Where collective.polls stores votes, why the REST API cannot change them, and how they survive an export."
    "property=og:title": "Vote storage"
    "keywords": "Plone, polls, votes, storage, plone.exportimport, REST API"
---

# Vote storage

## Votes are not content fields

A poll's settings are fields, edited in its form and changed through the content REST API like any other content.
Its votes are not.
They are stored beside the poll, as a count for each option id and the set of voter ids, and only the voting code writes them.

This keeps the results honest.
If votes were a field, anyone who can edit the poll could rewrite its results with a `PATCH` request, and a form saved at the wrong moment could overwrite votes cast while it was open.
Instead, a vote can only be added, by `@vote`, by someone allowed to vote, once.

## Votes follow option ids

Votes are counted per option id, not per position or description.
Each option keeps its id when the options are reordered or edited, and a new option gets the next id after the highest one in the poll.
So reordering a poll's options, or rewording one, never moves votes from one option to another.

Votes for an option that was removed are kept.
They no longer appear in the results, but nothing recorded is ever lost.

## Rejecting a poll clears it

Sending an open poll back to *Private* removes all its votes.
A rejected poll is being reworked, and its options may change, so votes cast for the earlier version would no longer mean anything.

## Exporting votes

`plone.exportimport` moves content between sites by serializing it, and importing it back.
The add-on carries a closed poll's votes along, under the key `collective.polls.votes` in the poll's exported data.

```json
"collective.polls.votes": {
  "counts": {"0": 2, "1": 1},
  "voters": ["Anonymous-3f9a", "jane"]
}
```

The serializer that adds them and the deserializer that writes them are registered only for requests that `plone.exportimport` marks as its own.
A REST API call is never marked, so it can neither read the votes through `GET` nor write them through `PATCH` or `POST`.
This keeps the rule above: outside an import, votes come only from voters.

Only closed polls carry their votes.
A closed poll's results are final, so the export is a faithful copy.
An open poll would keep collecting votes after the export, and importing that snapshot would silently drop them.
