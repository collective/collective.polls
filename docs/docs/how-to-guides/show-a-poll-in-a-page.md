---
myst:
  html_meta:
    "description": "Show a poll in any page with the Poll block: the latest open poll of the site, or a poll you pick."
    "property=og:description": "Show a poll in any page with the Poll block: the latest open poll of the site, or a poll you pick."
    "property=og:title": "Show a poll in a page"
    "keywords": "Plone, Volto, polls, Poll block, grid"
---

# Show a poll in a page

The Poll block shows a poll in any page, and visitors can vote in it without leaving the page.
It works as a top-level block and inside a Grid block.

## Show the latest open poll

Use this to keep a page showing whatever poll is current.

1.  Edit the page, and add a **Poll** block.
2.  In the block's settings, keep **Which poll** at **Latest opened poll**.
3.  Optionally, check **Show closed polls**, so that the block shows the results of the latest closed poll while no poll is open.
4.  Save the page.

The block searches the whole site, or the whole language folder in a multilingual site, and shows the newest poll by creation date.
It shows nothing to visitors when there is no poll to show.

```{image} /_static/screens/poll-block-settings.png
:alt: The settings of a Poll block in the sidebar: Which poll, Show closed polls, Header, Show total votes, and Add a link to the poll
```

## Show a chosen poll

1.  Edit the page, and add a **Poll** block.
2.  Set **Which poll** to **A chosen poll**.
3.  In **Chosen poll**, browse to the poll and select it.
4.  Save the page.

The block keeps showing that poll in any state the visitor can see: its options while it is not open yet, the vote form while it is open, and its results once it is closed.

## Adjust what the block shows

| Setting | Effect |
|---|---|
| **Header** | A heading above the poll. Leave it empty for none. |
| **Show total votes** | Show how many votes the poll collected, when the visitor may see the results. |
| **Add a link to the poll** | Link the poll's question to the poll itself. |

See {doc}`/reference/poll-block` for the stored values.
