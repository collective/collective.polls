---
myst:
  html_meta:
    "description": "The frontend pieces of @plone-collective/volto-polls that a project can replace or reuse."
    "property=og:description": "The frontend pieces of @plone-collective/volto-polls that a project can replace or reuse."
    "property=og:title": "Frontend components"
    "keywords": "Plone, Volto, polls, component registry, Poll, PollResultsGraph"
---

# Frontend components

The add-on registers these components in Volto's component registry.
See {doc}`/how-to-guides/customize-the-frontend` to replace them.

| Name | Dependencies | Is |
|---|---|---|
| `Poll` | none | The poll itself: its question, status messages, vote form, and results. The poll view and the Poll block both use it. |
| `PollResultsGraph` | `bar`, `pie`, or `numbers` | The chart for one graph type. |

## `Poll`

| Property | Type | Description |
|---|---|---|
| `path` | string | The poll's path, relative to the site. Required. |
| `title` | string | The question, shown as a heading. The poll view leaves it out, because the page title already says it. |
| `header` | string | A heading above the poll. |
| `showTotal` | boolean | Show the number of votes so far, when the user may see the results. |
| `linkToPoll` | boolean | Link the question to the poll. |
| `interactive` | boolean | `false` shows the poll without letting anyone vote, as in the block editor. |
| `fallbackOptions` | list | Options to show until the poll's state arrives, such as when rendering on the server. |
| `fallbackMaxChoices` | number | How many options a voter can pick, until the poll's state arrives. |
| `fallbackLegend` | string or `null` | The legend, until the poll's state arrives. |

## `PollResultsGraph`

| Property | Type | Description |
|---|---|---|
| `results` | list | The results, in the poll's option order, as the `results` of the `@poll` service. |

A graph type without a registered component is drawn as `numbers`.

## Other pieces

| Piece | Name |
|---|---|
| Poll view | The default view of `collective.polls.poll`. |
| Options widget | The `poll_options` widget, which edits a poll's options. |
| Content icon | A bar chart icon for `collective.polls.poll`, in the `contentIcons` setting. |
