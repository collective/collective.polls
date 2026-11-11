---
block: poll
---

Shows a poll in a page or a grid: the latest open poll of the site section, or a poll chosen by the editor. Visitors vote in the block when the poll allows it, and see its results as the poll's own settings say.

The block stores only its settings. It does not store the question, the options, the votes or the state of the poll: it reads them from the poll when it renders, so to change what the block shows, change the poll.

### Fields

- `mode`: `latest` (the default) shows the most recently opened poll of the site section. `chosen` shows the poll named in `poll`.
- `poll`: a list with at most one `{ "@id": path }` object, where `path` is the path or full URL of a `collective.polls.poll` item. Used only when `mode` is `chosen`.
- `show_closed`: `true` or `false` (the default). Used only when `mode` is `latest`. When no poll is open, `true` shows the results of the latest closed poll instead of nothing.
- `display`: `poll` (the default) shows the question and its options. `results` shows only the results, to place them apart from the vote. They appear only when the poll lets the visitor see them.
- `header`: a string shown above the poll. Leave it out for no header.
- `show_total`: `true` (the default) or `false`. Shows the number of votes collected so far.
- `link_poll`: `true` (the default) or `false`. Adds a link to the poll's own page.

### Examples

A block that shows the latest open poll:

```json
{
  "@type": "poll"
}
```

A block that shows the results of a chosen poll, with a header:

```json
{
  "@type": "poll",
  "mode": "chosen",
  "poll": [{ "@id": "/polls/favourite-language" }],
  "display": "results",
  "header": "Results",
  "show_total": true,
  "link_poll": true
}
```

A block that shows the latest closed poll when no poll is open:

```json
{
  "@type": "poll",
  "mode": "latest",
  "show_closed": true
}
```

### Not stored in the block

The question, the options, the votes, the deadline and the workflow state of the poll are all stored on the poll item. An agent that needs to know what a poll asks must read the poll, not look for those values in this block.
