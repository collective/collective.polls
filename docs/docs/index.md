---
myst:
  html_meta:
    "description": "A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users."
    "property=og:description": "A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users."
    "property=og:title": "collective.polls"
    "keywords": "Plone, Volto, polls, voting, collective.polls"
---

# collective.polls

A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users.

A poll asks one question with two or more options.
Editors decide whether visitors pick one option or several, whether anonymous visitors may vote, whether voters see partial results, and how to draw the results.
The poll moves through its own workflow: it collects votes only while open, and shows its final results once closed.

```{image} /_static/screens/home-poll-blocks.png
:alt: A page with three Poll blocks in a grid: a multiple choice poll, a single choice poll, and a closed poll showing its results as a pie chart
```

## Two add-ons, installed together

| Package | Is | Gives you |
|---|---|---|
| `collective.polls` | A Plone backend add-on | The Poll content type and its workflow, vote storage, the `@poll` and `@vote` REST services, and an upgrade step from version 2.x. |
| `@plone-collective/volto-polls` | A Volto frontend add-on | The poll view, the Poll block, and the widget that edits a poll's options. |

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} 🧭 How-to guides
:link: how-to-guides/index
:link-type: doc

Install the add-ons and get a result.
````

````{grid-item-card} 🚀 Tutorials
:link: tutorials/index
:link-type: doc

Learn by doing.
````

````{grid-item-card} 📖 Reference
:link: reference/index
:link-type: doc

The REST services, settings, and other technical descriptions.
````

````{grid-item-card} 💡 Concepts
:link: concepts/index
:link-type: doc

Why the add-on works the way it does.
````
`````

## What you need

| | |
|---|---|
| Plone | 6.2 |
| Python | {SUPPORTED_PYTHON_VERSIONS} |
| Frontend | Volto 19 |

```{toctree}
:maxdepth: 2
:hidden: true

how-to-guides/index
tutorials/index
reference/index
concepts/index
```

```{toctree}
:caption: Appendices
:maxdepth: 2
:hidden: true

glossary
genindex
```
