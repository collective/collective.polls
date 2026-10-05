<div align="center">

<h1 align="center">collective.polls</h1>

</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.polls)](https://pypi.org/project/collective.polls/)
[![npm](https://img.shields.io/npm/v/@plone-collective/volto-polls)](https://www.npmjs.com/package/@plone-collective/volto-polls)

[![Built with Cookieplone](https://img.shields.io/badge/built%20with-Cookieplone-0083be.svg?logo=cookiecutter)](https://github.com/plone/cookieplone-templates/)
[![Documentation](https://img.shields.io/badge/docs-collective.github.io-0083be)](https://collective.github.io/collective.polls/)

[![CI](https://github.com/collective/collective.polls/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective.polls/actions/workflows/main.yml)

</div>

A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users.

📖 **[Read the documentation](https://collective.github.io/collective.polls/)**

## What it does 📋

- **Polls as content.** A Poll asks one question with two or more options, and can hold the images it shows.
- **Single or multiple choice.** Editors set how many options a voter can pick, the legend shown above the options, and whether the options appear in a random order.
- **Anonymous or members only.** An open poll accepts votes from anonymous visitors when it allows them, and when visitors can see its parent folder: publish the folder before opening the poll. A cookie keeps an anonymous visitor from voting twice.
- **Results the editors choose.** Voters can see partial results after voting, and the results show as bars, a pie, or plain numbers. In a multiple choice poll, each percentage is the share of voters who picked the option, and a pie shows as bars.
- **A Volto block.** The Poll block shows the latest open poll of the site section, the latest closed one when none is open, or a poll the editor picks. It also works inside a Grid.
- **A REST API.** `GET @poll` answers the state of a poll for the current user, and `POST @vote` records a vote.
- **Export and import.** With `plone.exportimport`, a closed poll's votes go out with its content and come back on import. The REST API never reads or writes them.
- **An upgrade from 2.x.** The upgrade step moves the stored votes to the new storage, and removes the voting portlets, which the Poll block replaces.

## Workflow 🔄

Polls have their own workflow, with the states *Private*, *Pending review*, *Open*, and *Closed*.

- A new poll is *Private*. Its owner, editors, managers, and site administrators can change it.
- From *Private*, a poll goes to *Pending review*, or straight to *Open* for someone who can review content.
- While *Pending review*, managers, reviewers, and site administrators can change it. A reviewer opens it, or sends it back to *Private*.
- An *Open* poll collects votes, and nobody can change it.
- Reviewers, managers, and site administrators close an *Open* poll, or send it back to *Private*. Sending it back removes all of its votes.
- A *Closed* poll shows its final results. Nobody can change it or vote in it, and it can be opened again.

## Documentation 📚

The documentation lives at [collective.github.io/collective.polls](https://collective.github.io/collective.polls/), and its sources in [`docs/`](./docs/).

To build it locally, run the following commands.

```shell
make docs-install
make docs-build
```

## Install in your project 🔧

The add-on comes in two packages, and a site needs both.

### Backend

Add `collective.polls` to your project's dependencies, then install it in your Plone site from the **Add-ons** control panel.

```shell
uv add collective.polls
```

### Frontend

Add `@plone-collective/volto-polls` to your Volto project.

```shell
pnpm add @plone-collective/volto-polls
```

Then list it in the `addons` of your `volto.config.js`.

```javascript
const addons = ['@plone-collective/volto-polls'];
```

## Quick Start 🏁

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
-   [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 24
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective.polls.git
    cd collective.polls
    ```

2.  Install this code base.

    ```shell
    make install
    ```

### Fire Up the Servers 🔥

1.  Create a new Plone site on your first run.
    It comes with example content, including polls.

    ```shell
    make backend-create-site
    ```

2.  Start the backend at http://localhost:8080/.

    ```shell
    make backend-start
    ```

3.  In a new shell session, start the frontend at http://localhost:3000/.

    ```shell
    make frontend-start
    ```

### Local Stack Deployment 📦

Deploy a local Docker Compose environment that includes the following.

- Docker images for the backend and the frontend 🖼️
- A stack with a Traefik router and a PostgreSQL database 🗃️
- Accessible at [http://collective.polls.localhost](http://collective.polls.localhost) 🌐

Run the following commands in a shell session.

```shell
make stack-create-site
make stack-start
```

## Project structure 🏗️

This monorepo consists of the following sections.

- **backend**: The `collective.polls` Plone add-on, installed with uv instead of buildout.
- **frontend**: The `@plone-collective/volto-polls` Volto add-on.
- **docs**: The documentation, built with Sphinx and the Plone Sphinx Theme.

### Why this structure? 🤔

- Everything needed to run a site with the add-on is in the repository.
- Each section has its own GitHub workflows, which run only when it changes (see `.github/workflows`).
- It makes building a Docker image for each section simple.

## Code quality assurance 🧐

To check your code against quality standards, run the following shell command.

```shell
make check
```

### Format the codebase

To format and rewrite the code base, ensuring it adheres to quality standards, run the following shell command.

```shell
make format
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Python code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | `zpretty` | XML and ZCML formatting  | -- |
| frontend | ESLint | Fixes most common frontend issues | [`frontend/.eslintrc.js`](./frontend/.eslintrc.js) |
| frontend | prettier | Format JS and Typescript code  | [`frontend/.prettierrc`](./frontend/.prettierrc) |
| frontend | Stylelint | Format Styles (css, less, sass)  | [`frontend/.stylelintrc`](./frontend/.stylelintrc) |

Formatters can also be run within the `backend` or `frontend` folders.

### Linting the codebase

To check the code base without changing it, run the following shell command.

```shell
make lint
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Checks code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | Pyroma | Checks Python package metadata  | -- |
| backend | check-python-versions | Checks Python version information  | -- |
| backend | `zpretty` | Checks XML and ZCML formatting  | -- |
| frontend | ESLint | Checks JS / Typescript lint | [`frontend/.eslintrc.js`](./frontend/.eslintrc.js) |
| frontend | prettier | Check JS / Typescript formatting  | [`frontend/.prettierrc`](./frontend/.prettierrc) |
| frontend | Stylelint | Check Styles (css, less, sass) formatting  | [`frontend/.stylelintrc`](./frontend/.stylelintrc) |

Linters can be run individually within the `backend` or `frontend` folders.

## Internationalization 🌐

Generate the translation files for Plone and Volto with the following command.

```shell
make i18n
```

## Packages 📦

| Package | Description |
| --- | --- |
| [`collective.polls`](./backend/) | The Plone backend add-on. |
| [`@plone-collective/volto-polls`](./frontend/packages/volto-polls/) | The Volto frontend add-on. |

Got an idea? Found a bug? Let us know by [opening an issue](https://github.com/collective/collective.polls/issues).

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
