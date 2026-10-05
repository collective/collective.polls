---
myst:
  html_meta:
    "description": "Add the @plone-collective/volto-polls add-on to a Volto project."
    "property=og:description": "Add the @plone-collective/volto-polls add-on to a Volto project."
    "property=og:title": "Install the frontend"
    "keywords": "Plone, Volto, polls, install, frontend, pnpm"
---

(how-to-install-frontend)=

# Install the frontend

Add `@plone-collective/volto-polls` to a Volto project.

Without it the backend stores polls, but nobody can see or vote in them: the poll view, the Poll block, and the options widget all come from the frontend add-on.

Do {doc}`backend` first.

## Requirements

| | |
|---|---|
| Volto | 19 |
| Package manager | pnpm |

## Add the add-on

A [Cookieplone](https://github.com/plone/cookieplone) project has an add-on package of its own under `frontend/packages/`, and that package is where a project's add-ons are declared.
Volto loads it from `volto.config.js`, and everything it names comes with it, so `volto.config.js` is not edited here.

1.  Edit `frontend/packages/<your-addon>/package.json`, naming `@plone-collective/volto-polls` in **both** keys.

    ```json
    {
      "addons": [
        "@plone-collective/volto-polls"
      ],
      "dependencies": {
        "@plone-collective/volto-polls": "*"
      }
    }
    ```

    The two do different jobs, and one without the other fails quietly.
    `dependencies` is what fetches the package.
    `addons` is what Volto reads to register it: an add-on only in `dependencies` is installed and never loaded, so polls have no view and there is no Poll block.

2.  Install.

    ```shell
    make frontend-install
    ```

    Or from the frontend directory.

    ```shell
    cd frontend && make install
    ```

3.  Start.

    ```shell
    make frontend-start
    ```

    Or.

    ```shell
    cd frontend && make start
    ```

## Verify

Open any poll on the frontend.
It shows its options, and a **Vote** button while it is open.

If the page shows no options and no **Vote** button, the add-on is not registered.
Check that it is in the `addons` key of your add-on's `package.json`, not only in `dependencies`, and re-run `make frontend-install`.

Then edit a page, and check that **Poll** is in the list of blocks.

## What the add-on registers

| Piece | Is |
|---|---|
| Poll view | The default view of the `collective.polls.poll` type. |
| Poll block | The `poll` block, also allowed inside Grid blocks. |
| `poll_options` widget | Edits a poll's options. |
| Content icon | A bar chart for the Poll type. |
| `Poll`, `PollResultsGraph` | Components a project can replace. |

The full surface is in {doc}`/reference/frontend`.

## Next steps

1.  {doc}`/tutorials/first-poll`: create, open, and close a poll.
2.  {doc}`/how-to-guides/show-a-poll-in-a-page`: show polls with the Poll block.
3.  {doc}`/how-to-guides/customize-the-frontend`: replace how polls look.
