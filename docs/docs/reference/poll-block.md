---
myst:
  html_meta:
    "description": "The Poll block of @plone-collective/volto-polls: its settings and the data it stores."
    "property=og:description": "The Poll block of @plone-collective/volto-polls: its settings and the data it stores."
    "property=og:title": "The Poll block"
    "keywords": "Plone, Volto, polls, Poll block, block settings"
---

# The Poll block

| | |
|---|---|
| Block type | `poll` |
| Title | Poll |
| Allowed in | Pages and other blocks-enabled content, and Grid blocks |

## Settings

| Key | Setting | Default | Description |
|---|---|---|---|
| `mode` | Which poll | `latest` | `latest` for the latest opened poll, `chosen` for a poll the editor picks. |
| `poll` | Chosen poll | none | The picked poll, when `mode` is `chosen`. Only polls can be picked. |
| `show_closed` | Show closed polls | `false` | When `mode` is `latest` and no poll is open, show the latest closed poll. |
| `header` | Header | empty | A heading above the poll. |
| `show_total` | Show total votes | `true` | Show the number of votes so far, when the visitor may see the results. |
| `link_poll` | Add a link to the poll | `true` | Link the question to the poll. |

## Finding the latest poll

With `mode` set to `latest`, the block searches the navigation root for polls, newest first by creation date.
It searches for an open poll, then for a closed one when `show_closed` is set and no poll is open.

## When there is nothing to show

Visitors see nothing.
Editors see "There is no poll to show." while they edit the page.
