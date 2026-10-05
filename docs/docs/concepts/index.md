---
myst:
  html_meta:
    "description": "Concepts behind collective.polls: who can vote, how votes are counted, and how they are stored."
    "property=og:description": "Concepts behind collective.polls: who can vote, how votes are counted, and how they are stored."
    "property=og:title": "Concepts"
    "keywords": "Plone, polls, concepts, voting, results, vote storage"
---

# Concepts

Concept pages explain why the add-ons work the way they do.
Read them to understand a behavior, rather than to get a task done.

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} 🗳️ Voting and results
:link: voting-and-results
:link-type: doc

Who can vote, how a second vote is refused, how votes are counted, and who sees the results.
````

````{grid-item-card} 🗄️ Vote storage
:link: vote-storage
:link-type: doc

Where votes live, why the REST API cannot change them, and how they survive an export.
````
`````

```{toctree}
:maxdepth: 1
:hidden: true

voting-and-results
vote-storage
```
