---
myst:
  html_meta:
    "description": "Reference for collective.polls: the content type, workflow, REST API, Poll block, frontend components, Python API, and upgrade steps."
    "property=og:description": "Reference for collective.polls: the content type, workflow, REST API, Poll block, frontend components, Python API, and upgrade steps."
    "property=og:title": "Reference"
    "keywords": "Plone, Volto, polls, reference, REST API, workflow, content type"
---

# Reference

Reference pages describe the machinery: every field, state, endpoint, and setting.
They say what things are, not how to use them for a goal; for that, see {doc}`/how-to-guides/index`.

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} 🗳️ The Poll content type
:link: content-type
:link-type: doc

Fields, fieldsets, options, and validation rules.
````

````{grid-item-card} 🔄 Workflow and permissions
:link: workflow
:link-type: doc

States, transitions, and who can see, change, and vote.
````

````{grid-item-card} 🔌 REST API
:link: rest-api
:link-type: doc

The `@poll` and `@vote` services, their errors, and caching.
````

````{grid-item-card} 🧱 The Poll block
:link: poll-block
:link-type: doc

The block's settings and how it finds the latest poll.
````

````{grid-item-card} ⚛️ Frontend components
:link: frontend
:link-type: doc

What the Volto add-on registers, and what you can replace.
````

````{grid-item-card} 🐍 Python API
:link: python-api
:link-type: doc

The `IPolls` utility, the `IPollVotes` adapter, and the `Poll` class.
````

````{grid-item-card} ⬆️ Upgrade steps
:link: upgrade-steps
:link-type: doc

What the upgrade from 2.x does.
````
`````

```{toctree}
:maxdepth: 1
:hidden: true

content-type
workflow
rest-api
poll-block
frontend
python-api
upgrade-steps
```
