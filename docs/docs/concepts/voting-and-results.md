---
myst:
  html_meta:
    "description": "How collective.polls decides who can vote, refuses a second vote, counts votes, and shows results."
    "property=og:description": "How collective.polls decides who can vote, refuses a second vote, counts votes, and shows results."
    "property=og:title": "Voting and results"
    "keywords": "Plone, polls, voting, anonymous, results, multiple choice, caching"
---

# Voting and results

## Who can vote

Voting is a permission, `collective.polls: Vote`, and the workflow grants it only while a poll is *Open*.
Every logged-in role gets it then, so any member can vote in an open poll they can see.

Anonymous visitors are different.
The workflow cannot grant them the permission on its own, because whether they may vote depends on two things the workflow does not know: the poll's **Allow anonymous** setting, and whether anonymous visitors can see the poll at all.
So the add-on grants it when the poll is opened, and only when both hold: the poll allows anonymous votes, and its folder is the site root or is visible to anonymous visitors.

This is why the order matters: publish the folder, then open the poll.
A poll opened inside a private folder stays closed to anonymous visitors even after the folder is published, until the poll is opened again.
The `@poll` service reports that case as `anonymous_blocked`.

## Voting once

Each poll records who voted, and refuses a second vote from the same voter.

-   A member is recorded by their user id.
-   An anonymous visitor gets a random id, recorded as `Anonymous-` followed by it, and sent back in a cookie that lasts one year.
    Their next vote is refused when the browser sends the cookie back.

The cookie is the only thing that recognizes an anonymous visitor.
Clearing it, or using another browser, lets them vote again.
That is the trade-off of anonymous voting: polls that must count each person once should not allow it.

When the add-on cannot tell whether someone voted, it assumes they did.
That happens for an anonymous visitor on a poll that does not allow anonymous votes, or in code that votes without a request to read the cookie from.

## Counting votes

In a single choice poll, each voter adds one vote to one option, and the percentages are shares of all votes: they add up to 100.

In a multiple choice poll, a voter picks from 1 to the poll's limit, and adds one vote to each option picked.
The total is the number of voters, not the number of votes, and each percentage is the share of voters who picked that option.
The percentages can add up to more than 100: when everyone picks two options, they add up to 200.

That is why a multiple choice poll set to a pie chart shows bars: a pie shows parts of one whole, and these shares are not.

```{image} /_static/screens/poll-multiple-choice.png
:alt: A multiple choice poll, Away team, whose legend says Select up to 2 options above a list of checkboxes
```

## Who sees the results

| Who | Sees the results |
|---|---|
| Everyone, once the poll is closed | Always |
| Reviewers and managers | Always, in any state |
| Voters, while the poll is open | Only when **Show partial results** is on |
| Members who did not vote | Not while the poll is open |

```{image} /_static/screens/poll-closed-results.png
:alt: A closed poll, Choose a Captain, saying This poll is closed above its results as a pie chart
```

## Why anonymous answers do not say who voted

The `@poll` service gives every anonymous visitor the same answer, so a proxy or CDN can cache it and serve many visitors from one request.
That answer cannot say whether a particular visitor voted.
It includes the results whenever a voter would see them, and the browser decides, from the cookie, whether to show the results or the vote form.

Members get an answer of their own, which says whether they voted and is never cached.
