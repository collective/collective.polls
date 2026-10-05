# Polls for Plone 🚀

[![Built with Cookieplone](https://img.shields.io/badge/built%20with-Cookieplone-0083be.svg?logo=cookiecutter)](https://github.com/plone/cookieplone-templates/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/collective/collective.polls/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective.polls/actions/workflows/main.yml)

Online polls support for Plone and Volto.

## Features

- Polls can be opened for anonymous users to vote.
- If an open poll is allowed for anonymous but is inside a private folder,
  nobody can vote. Therefore the poll's parent folder needs to be published
  before opening the poll in order for this field to take effect.
- Voting can take place either in the object or in a voting portlet.
- The voting portlet can show the latest open poll or a specific open poll
  and closed polls.
- Users can see partial results of the poll.
- Results can be shown using a bar chart, a pie chart, or just by number of
  votes.

## Workflow

The workflow associated with polls has the following states: 'Private',
'Pending review', 'Open' and 'Closed'.

- Polls are created in 'Private' state; only Owner, Manager, Editor or Site
  Administrator roles can modify them.
- When a poll is in 'Private' state it can be sent to 'Pending review' or
  directly to 'Open' state, if the user has the proper role (Reviewer, Manager
  or Site Administrator).
- When a poll is in 'Pending review' state it can be edited by Manager,
  Reviewer or Site Administrator roles.
- A poll in 'Pending review' state can be sent to 'Open' state, with "Review
  portal content" permission, or to Private, with "Request review" permission.
- When the poll is 'Open' users can only vote; nobody can modify the poll in
  any way.
- An 'Open' poll can be sent to 'Private' or 'Closed' state by Reviewer,
  Manager or Site Administrator roles.
- When an 'Open' poll is sent to 'Private', all votes are removed to avoid
  data manipulation.
- When a poll is in 'Closed' state nobody can modify it, nor can anyone vote
  on it; a closed poll can always be reopened by users with proper
  permissions.

Got an idea? Found a bug? Let us know by [opening an issue](https://github.com/collective/collective.polls/issues).
See the [complete list of bugs on GitHub](https://github.com/collective/collective.polls/labels/bug).

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

Voila! Your Plone site should be live and kicking! 🎉

### Local Stack Deployment 📦

Deploy a local Docker Compose environment that includes the following.

- Docker images for Backend and Frontend 🖼️
- A stack with a Traefik router and a PostgreSQL database 🗃️
- Accessible at [http://collective.polls.localhost](http://collective.polls.localhost) 🌐

Run the following commands in a shell session.

```shell
make stack-create-site
make stack-start
```

And... you're all set! Your Plone site is up and running locally! 🚀

## Project structure 🏗️

This monorepo consists of the following distinct sections:

- **backend**: Houses the API and Plone installation, utilizing pip instead of buildout, and includes a policy package named collective.polls.
- **frontend**: Contains the React (Volto) package.
- **devops**: Encompasses Docker stack, Ansible playbooks, and cache settings.
- **docs**: Scaffold for writing documentation for your project.

### Why this structure? 🤔

- All necessary codebases to run the site are contained within the repository (excluding existing add-ons for Plone and React).
- Specific GitHub Workflows are triggered based on changes in each codebase (refer to .github/workflows).
- Simplifies the creation of Docker images for each codebase.
- Demonstrates Plone installation/setup without buildout.

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
| frontend | ESLint | Fixes most common frontend issues | [`frontend/.eslintrc.js`](.frontend/.eslintrc.js) |
| frontend | prettier | Format JS and Typescript code  | [`frontend/.prettierrc`](.frontend/.prettierrc) |
| frontend | Stylelint | Format Styles (css, less, sass)  | [`frontend/.stylelintrc`](.frontend/.stylelintrc) |

Formatters can also be run within the `backend` or `frontend` folders.

### Linting the codebase
or `lint`:

 ```shell
make lint
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Checks code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | Pyroma | Checks Python package metadata  | -- |
| backend | check-python-versions | Checks Python version information  | -- |
| backend | `zpretty` | Checks XML and ZCML formatting  | -- |
| frontend | ESLint | Checks JS / Typescript lint | [`frontend/.eslintrc.js`](.frontend/.eslintrc.js) |
| frontend | prettier | Check JS / Typescript formatting  | [`frontend/.prettierrc`](.frontend/.prettierrc) |
| frontend | Stylelint | Check Styles (css, less, sass) formatting  | [`frontend/.stylelintrc`](.frontend/.stylelintrc) |

Linters can be run individually within the `backend` or `frontend` folders.

## Internationalization 🌐

Generate translation files for Plone and Volto with ease:

```shell
make i18n
```

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
