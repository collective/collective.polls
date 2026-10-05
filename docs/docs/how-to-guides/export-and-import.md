---
myst:
  html_meta:
    "description": "Move polls and their votes between sites with plone.exportimport."
    "property=og:description": "Move polls and their votes between sites with plone.exportimport."
    "property=og:title": "Export and import polls"
    "keywords": "Plone, polls, plone.exportimport, export, import, votes"
---

# Export and import polls

[`plone.exportimport`](https://github.com/plone/plone.exportimport) exports a site's content to files, and imports it into another site.
With `collective.polls` installed in both sites, the votes of closed polls travel with them.

## Export a site

Run the exporter against the site's Zope configuration, its id, and a target folder.

```shell
plone-exporter instance/etc/zope.conf Plone /path/to/export
```

Every poll is exported with its settings and options.
A *Closed* poll also carries its votes: the count for each option, and the ids of the people who voted.

## Import into another site

Install `collective.polls` in the target site first, then run the importer.

```shell
plone-importer instance/etc/zope.conf Plone /path/to/export
```

The imported closed polls have the same results as in the original site, and the same voters cannot vote again when a poll is reopened.

## What is not exported

-   **Votes of polls that are not closed.** An open poll is still changing, so its export would be out of date by the time it is imported.
    Close a poll before exporting it to keep its votes.
-   **Anonymous voters' cookies.** They live in visitors' browsers.
    An anonymous voter is still counted, but would be able to vote again in a reopened poll.

## Why the content API leaves votes alone

Votes are read and written only by the export and the import, never by the content API.
See {doc}`/concepts/vote-storage` for the reasons.
