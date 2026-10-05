# collective.polls

A content type, workflow, and Volto block for conducting online polls in Plone, for anonymous and logged-in users.

This is the Plone backend add-on.
Its Volto frontend is [`@plone-collective/volto-polls`](https://www.npmjs.com/package/@plone-collective/volto-polls), and a site needs both.

## Features

- **The Poll content type.** A question with two or more options, which can hold the images it shows.
- **Single or multiple choice.** How many options a voter can pick, the legend shown above them, and whether they appear in a random order.
- **Anonymous voting.** An open poll accepts anonymous votes when it allows them and visitors can see its parent folder. A cookie keeps an anonymous visitor from voting twice.
- **A workflow of its own.** *Private*, *Pending review*, *Open*, and *Closed*. Votes are collected only while open, and sending an open poll back to *Private* removes them.
- **A REST API.** `GET @poll` answers the state of a poll for the current user, and `POST @vote` records a vote, as `{"option_id": 0}` or `{"option_ids": [0, 2]}`.
- **Export and import.** With `plone.exportimport`, a closed poll's votes go out with its content and come back on import. The REST API never reads or writes them.
- **An upgrade from 2.x.** The upgrade step moves the stored votes to the new storage and removes the voting portlets.
- **Translations** in Catalan, Czech, German, Spanish, Finnish, French, Italian, Dutch, Brazilian Portuguese, and Traditional Chinese.

## Documentation

Read the documentation at [collective.github.io/collective.polls](https://collective.github.io/collective.polls/).

## Installation

Add `collective.polls` to your project's dependencies.

```shell
uv add collective.polls
```

Then install it in your Plone site from the **Add-ons** control panel.

### Upgrading from 2.x

Version 3 requires Plone 6.2.
After upgrading the package, run the upgrade steps from the **Add-ons** control panel.

## Contribute

- [Issue tracker](https://github.com/collective/collective.polls/issues)
- [Source code](https://github.com/collective/collective.polls/)

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository.

    ```shell
    git clone git@github.com:collective/collective.polls.git
    cd collective.polls/backend
    ```

2.  Install this code base.

    ```shell
    make install
    ```

3.  Create a Plone site with example content, then start it at http://localhost:8080/.

    ```shell
    make create-site
    make start
    ```

### Tests

Run the test suite, with or without a coverage report.

```shell
make test
make test-coverage
```

Check the code, and its type annotations.

```shell
make lint
make typecheck
```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
