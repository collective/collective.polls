# collective.polls (@plone-collective/volto-polls)

A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users.

This is the Volto frontend add-on.
Its Plone backend is [`collective.polls`](https://pypi.org/project/collective.polls/), and a site needs both.

[![npm](https://img.shields.io/npm/v/@plone-collective/volto-polls)](https://www.npmjs.com/package/@plone-collective/volto-polls)
[![Documentation](https://img.shields.io/badge/docs-collective.github.io-0083be)](https://collective.github.io/collective.polls/)
[![CI](https://github.com/collective/collective.polls/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective.polls/actions/workflows/main.yml)

## Features

- **The poll view.** The view of the `collective.polls.poll` content type: the vote form while the visitor can vote, the results otherwise.
- **The Poll block.** Shows the latest open poll of the site section, the latest closed one when none is open, or a poll the editor picks. It also works inside a Grid.
- **Single or multiple choice.** Radio buttons or checkboxes, under the poll's legend or a default one, in the poll's order or a random one.
- **Results as bars, a pie, or numbers.** Each chart comes with a table for assistive technology.
- **An options widget.** Editors add, remove, and reorder a poll's options, and each option keeps its id, so its votes stay with it.
- **Translations** in Catalan, Czech, German, Spanish, Finnish, French, Dutch, Brazilian Portuguese, and Traditional Chinese.

### Customizing

The add-on registers its pieces in the component registry, so a project can replace them without shadowing files.

| Name | Dependencies | Is |
| --- | --- | --- |
| `Poll` | -- | The poll itself, used by both the view and the block. |
| `PollResultsGraph` | `bar`, `pie`, or `numbers` | The chart for one kind of results. |

## Documentation

Read the documentation at [collective.github.io/collective.polls](https://collective.github.io/collective.polls/).

## Installation

This add-on requires Volto 19.

Add `@plone-collective/volto-polls` to your project.

```shell
pnpm add @plone-collective/volto-polls
```

Then list it in the `addons` of your `volto.config.js`.

```javascript
const addons = ['@plone-collective/volto-polls'];
```

## Test installation

Visit http://localhost:3000/ in a browser, log in, and add a Poll.

## Development

The development of this add-on is done in isolation using pnpm workspaces, the latest `mrs-developer`, and other Volto core improvements.
For these reasons, it only works with pnpm and Volto 19.

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
-   [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 24
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective.polls.git
    cd collective.polls/frontend
    ```

2.  Install this code base.

    ```shell
    make install
    ```

### Make convenience commands

Run `make help` to list the available Make commands.

### Start developing

Start the backend.

```shell
make backend-docker-start
```

In a separate terminal session, start the frontend.

```shell
make start
```

### Lint code

Run ESlint, Prettier, and Stylelint in analyze mode.

```shell
make lint
```

### Format code

Run ESlint, Prettier, and Stylelint in fix mode.

```shell
make format
```

### Type check

Run the TypeScript compiler without emitting files.

```shell
make typecheck
```

### i18n

Extract the i18n messages to locales.

```shell
make i18n
```

### Unit tests

Run the unit tests once.

```shell
make ci-test
```

`make test` runs them in watch mode instead, and never returns.

### Storybook

Build Storybook, or start it while you work.

```shell
make storybook-build
make storybook-start
```

### Run Cypress tests

Run each of these steps in separate terminal sessions.

In the first session, start the frontend in development mode.

```shell
make acceptance-frontend-dev-start
```

In the second session, start the backend acceptance server.

```shell
make acceptance-backend-start
```

In the third session, start the Cypress interactive test runner.

```shell
make acceptance-test
```

## License

The project is licensed under the MIT license.
