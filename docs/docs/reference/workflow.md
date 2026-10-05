---
myst:
  html_meta:
    "description": "The poll workflow of collective.polls: its states, transitions, and permissions."
    "property=og:description": "The poll workflow of collective.polls: its states, transitions, and permissions."
    "property=og:title": "Workflow and permissions"
    "keywords": "Plone, polls, workflow, permissions, vote, roles"
---

# Workflow and permissions

Polls use their own workflow, `poll_workflow`.

```{mermaid}
stateDiagram-v2
    direction LR
    [*] --> private
    private --> pending: Submit for opening
    pending --> private: Retract
    private --> open: Open
    pending --> open: Open
    pending --> private: Reject
    open --> closed: Close
    open --> private: Reject, removes every vote
    closed --> open: Open

    private: Private
    pending: Pending review
    open: Open, collects votes
    closed: Closed, shows final results
```

## States

| State | Id | Who can see it | Who can change it | Who can vote |
|---|---|---|---|---|
| Private | `private` | Owner, Reader, Contributor, Editor, Manager, Site Administrator | Owner, Editor, Manager, Site Administrator | Nobody |
| Pending review | `pending` | The roles of *Private*, and Reviewer | Manager, Reviewer, Site Administrator | Nobody |
| Open | `open` | Whoever can see the poll's folder | Nobody | Member, Reader, Contributor, Editor, Reviewer, Manager, Site Administrator; and Anonymous, see below |
| Closed | `closed` | Whoever can see the poll's folder | Nobody | Nobody |

A new poll starts *Private*.

## Transitions

| Transition | Id | From | To | Guard permission |
|---|---|---|---|---|
| Submit for opening | `submit` | Private | Pending review | Request review |
| Retract | `retract` | Pending review | Private | Request review |
| Open | `open` | Private, Pending review, Closed | Open | Review portal content |
| Reject | `reject` | Pending review, Open | Private | Review portal content |
| Close | `close` | Open | Closed | `collective.polls: Close poll` |

Two transitions do more than change the state.

-   **Open** grants the vote permission to Anonymous on the poll, when the poll allows anonymous votes and its folder is the site root or is visible to Anonymous.
    The check happens only at that moment: publishing the folder later does not let anonymous visitors vote until the poll is opened again.
-   **Reject** removes every vote of the poll.

## Permissions

| Permission | Id | Granted by default to |
|---|---|---|
| `collective.polls: Add poll` | `collective.polls.AddPoll` | Manager, Site Administrator, Owner, Contributor |
| `collective.polls: Close poll` | `collective.polls.ClosePoll` | Manager, Site Administrator, Reviewer |
| `collective.polls: Vote` | `collective.polls.Vote` | Nobody; the workflow grants it on open polls |

Having the vote permission is not enough to vote twice: see {doc}`/concepts/voting-and-results`.
