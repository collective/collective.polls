---
myst:
  html_meta:
    "description": "What the upgrade from collective.polls 2.x to profile version 3000 does."
    "property=og:description": "What the upgrade from collective.polls 2.x to profile version 3000 does."
    "property=og:title": "Upgrade steps"
    "keywords": "Plone, polls, upgrade steps, GenericSetup, 3000"
---

# Upgrade steps

The profile version of `collective.polls` 3 is `3000`.
One upgrade goes there from any 2.x version, and it is safe to run more than once.
It never drops vote data.

| Step | What it does |
|---|---|
| Re-apply the browser layer, type, workflow and permissions | Imports the `browserlayer`, `typeinfo`, `workflow`, and `rolemap` steps. Without the browser layer, the REST services do not exist. |
| Move votes to the 3.0 storage | Copies each poll's 2.x vote counts and voters to the new storage, and gives options stable ids. |
| Remove vote portlets | Deletes every 2.x voting portlet assignment. |
| Let anonymous visitors vote in open polls again | Grants the vote to Anonymous on every open poll that allows anonymous votes and whose folder anonymous visitors can see. Reinstalling 2.x could have dropped that grant. |
| Remove registrations of 2.x tiles and resources | Removes the `collective.cover` tile and the JavaScript and CSS resources from the registry. |
| Check that `plone.volto` is installed | Logs a warning when it is not, because polls cannot be shown without Volto. It does not install it. |

See {doc}`/how-to-guides/install/upgrade` to run it.
