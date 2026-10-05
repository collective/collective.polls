---
myst:
  html_meta:
    "description": "Install the collective.polls backend and its Volto frontend, run the development environment, and upgrade from 2.x."
    "property=og:description": "Install the collective.polls backend and its Volto frontend, run the development environment, and upgrade from 2.x."
    "property=og:title": "Install and upgrade"
    "keywords": "Plone, Volto, polls, install, upgrade"
---

# Install and upgrade

Get polls running on a site, and keep it current.
A site needs both add-ons: install the backend first, then the frontend.

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} 🐍 Install the backend
:link: backend
:link-type: doc

Add `collective.polls` to a Plone 6.2 project and install its profile.
````

````{grid-item-card} ⚛️ Install the frontend
:link: frontend
:link-type: doc

Add `@plone-collective/volto-polls` to a Volto project.
````

````{grid-item-card} 🛠️ Run the development environment
:link: development
:link-type: doc

Run both add-ons from this repository, with example content.
````

````{grid-item-card} ⬆️ Upgrade from 2.x
:link: upgrade
:link-type: doc

Move a site's polls and votes to version 3.
````
`````

```{toctree}
:maxdepth: 1
:hidden: true

backend
frontend
development
upgrade
```
