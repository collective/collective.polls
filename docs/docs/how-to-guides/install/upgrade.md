---
myst:
  html_meta:
    "description": "Upgrade a site from collective.polls 2.x to 3.x: move the votes, replace the portlets with Poll blocks, and check anonymous voting."
    "property=og:description": "Upgrade a site from collective.polls 2.x to 3.x: move the votes, replace the portlets with Poll blocks, and check anonymous voting."
    "property=og:title": "Upgrade from 2.x"
    "keywords": "Plone, Volto, polls, upgrade, migration, 2.x"
---

# Upgrade from 2.x

Version 3 keeps your polls and their votes, but changes how they are shown.
Read the whole guide before you start, and try it on a copy of your site first.

## What changes

-   **Plone 6.2 and Volto only.** The 2.x views, the voting portlet, the `collective.cover` tile, and their JavaScript and CSS are gone.
    Polls are shown by the Volto add-on, and the Poll block replaces the portlet.
-   **New vote storage.** Votes move from the old annotations to a storage of their own, with the same counts and voters.
-   **Stable option ids.** Each option keeps its id when the options are reordered, so its votes stay with it.
-   **Anonymous voters are not recognized anymore.** The 2.x cookie that marked them was set to expire in February 2020, so no browser still holds it, and visitors who voted anonymously could vote again in a poll that is still open.

See {doc}`/reference/upgrade-steps` for everything the upgrade does.

## Upgrade the site

1.  Back up the database.
2.  Upgrade the site to Plone 6.2, following the [Plone upgrade guide](https://6.docs.plone.org/backend/upgrading/index.html).
    The site must use Volto, with `plone.volto` installed.
3.  Update `collective.polls` to version 3 in your backend, and add `@plone-collective/volto-polls` to your frontend, as in {doc}`backend` and {doc}`frontend`.
4.  Restart the backend.
5.  Log in as a site administrator, open **Site Setup**, then **Add-ons**.
    **collective.polls** is listed under **Updates available**.
    Choose **Update**.

The upgrade logs what it did.
When `plone.volto` is not installed, it logs a warning: polls cannot be shown in that site until it is.

## Replace the portlets

The upgrade removes every voting portlet, because Volto does not show portlets.
For each page that showed one, add a Poll block where the portlet was, as described in {doc}`/how-to-guides/show-a-poll-in-a-page`.

The block has the settings the portlet had: the latest open poll or a chosen one, a header, the number of votes, and a link to the poll.

## Check anonymous voting

Anonymous visitors can vote in an open poll only when they can see its folder.
After the upgrade, open each poll that allows anonymous votes, and check that its folder is published.
The `@poll` service answers `"anonymous_blocked": true` for an open poll that should accept anonymous votes and cannot.
To fix one, publish its folder, then close the poll and open it again.
