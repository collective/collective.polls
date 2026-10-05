---
myst:
  html_meta:
    "description": "The Poll content type of collective.polls: its fields, fieldsets, options, and validation rules."
    "property=og:description": "The Poll content type of collective.polls: its fields, fieldsets, options, and validation rules."
    "property=og:title": "The Poll content type"
    "keywords": "Plone, polls, content type, fields, IPoll"
---

# The Poll content type

| | |
|---|---|
| Portal type | `collective.polls.poll` |
| Class | `collective.polls.content.poll.Poll`, a Dexterity container |
| Schema | `collective.polls.content.poll.IPoll` |
| Add permission | `collective.polls: Add poll` |
| Workflow | `poll_workflow`, see {doc}`workflow` |
| Allowed content | Images |
| Behaviors | `plone.basic`, `plone.namefromtitle`, `volto.preview_image_link`, `plone.shortname`, `plone.excludefromnavigation` |

The title is the poll's question, and the description is shown below it.

## Voting fieldset

| Field | Title | Type | Default | Description |
|---|---|---|---|---|
| `allow_anonymous` | Allow anonymous | Boolean | `true` | Lets anonymous visitors vote, when they can see the poll's folder at the moment the poll is opened. |
| `max_choices` | Number of options a voter can pick | Integer, at least 1 | `1` | `1` makes a single choice poll. A higher number lets each voter pick up to that many options. |
| `legend` | Legend | Text line | empty | Shown above the options. When empty, the form shows *Select one option* or *Select up to N options*. |
| `options` | Available options | JSON list | empty | The options, see {ref}`reference-options`. |
| `shuffle_options` | Shuffle options | Boolean | `false` | Shows the options in a random order to each voter. |

```{image} /_static/screens/poll-add-voting.png
:alt: The Voting tab of the form that adds a poll, with the options widget
```

## Results fieldset

| Field | Title | Type | Default | Description |
|---|---|---|---|---|
| `show_results` | Show partial results | Boolean | `true` | Lets voters see the results while the poll is open, once they voted. |
| `results_graph` | Graph | Choice | `bar` | How to draw the results: `bar` (Bar Chart), `pie` (Pie Chart), or `numbers` (Numbers Only). The vocabulary is `collective.polls.ResultsGraph`. |

```{image} /_static/screens/poll-add-results.png
:alt: The Results tab of the form that adds a poll: Show partial results, and Graph
```

(reference-options)=

## Options

Each option is stored as an object with an id and a description.

```json
[
  {"option_id": 0, "description": "Apple"},
  {"option_id": 1, "description": "Banana"}
]
```

-   An option that is saved without an `option_id` gets the next free id: one more than the highest id in the list, or `0` for the first.
-   An option keeps its id when the options are reordered or others are removed, so its votes stay with it.
-   Votes for a removed option are kept, but no longer counted in the results.

## Validation

A poll cannot be saved when any of these rules fails.

-   It has at least two options.
-   No two options share an id.
-   `max_choices` is not greater than the number of options.
