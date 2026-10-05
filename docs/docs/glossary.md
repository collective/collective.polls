---
myst:
  html_meta:
    "description": "Terms used throughout the collective.polls documentation."
    "property=og:description": "Terms used throughout the collective.polls documentation."
    "property=og:title": "Glossary"
    "keywords": "Plone, Volto, polls, glossary, term, definition"
---

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

Plone
    [Plone](https://plone.org/) is an open source content management system, used to create, edit, and manage websites, intranets, and custom solutions.

Volto
    [Volto](https://6.docs.plone.org/volto/index.html) is the React frontend for Plone 6.
    `@plone-collective/volto-polls` is a Volto add-on.

add-on
    A package that extends Plone.
    A backend add-on is a Python package, such as `collective.polls`; a frontend add-on is a JavaScript package, such as `@plone-collective/volto-polls`.

poll
    A content item of the type `collective.polls.poll`, which asks one question with two or more options.

option
    One of the answers a poll offers.
    Each option has an id, which never changes, and a description.

single choice poll
    A poll whose voters pick exactly one option: its **Number of options a voter can pick** is `1`.

multiple choice poll
    A poll whose voters pick from one option up to its **Number of options a voter can pick**.

partial results
    The results of a poll while it is still open.
    Voters see them when the poll's **Show partial results** setting is on.

Poll block
    A Volto block that shows a poll in any page, either the latest open one or one the editor picks.

anonymous voting
    Voting by visitors who are not logged in.
    A poll allows it with its **Allow anonymous** setting, and a cookie keeps each browser from voting twice.

plone.exportimport
    [`plone.exportimport`](https://github.com/plone/plone.exportimport) exports a Plone site's content to files, and imports it into another site.

workflow
    The states a content item goes through, and the transitions between them.
    Polls use their own workflow, with the states *Private*, *Pending review*, *Open*, and *Closed*.
```
