# collective.polls

Online polls support for Plone and Volto.

## Features

TODO: List our awesome features

## Installation

Install collective.polls with uv.

```shell
uv add collective.polls
```

Create the Plone site.

```shell
make create-site
```

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


### Add features using `plonecli` or `bobtemplates.plone`

This package provides markers as strings (`<!-- extra stuff goes here -->`) that are compatible with [`plonecli`](https://github.com/plone/plonecli) and [`bobtemplates.plone`](https://github.com/plone/bobtemplates.plone).
These markers act as hooks to add all kinds of features through subtemplates, including behaviors, control panels, upgrade steps, or other subtemplates from `bobtemplates.plone`.
`plonecli` is a command line client for `bobtemplates.plone`, adding autocompletion and other features.

To add a feature as a subtemplate to your package, use the following command pattern.

```shell
make add <template_name>
```

For example, you can add a content type to your package with the following command.

```shell
make add content_type
```

You can add a behavior with the following command.

```shell
make add behavior
```

```{seealso}
You can check the list of available subtemplates in the [`bobtemplates.plone` `README.md` file](https://github.com/plone/bobtemplates.plone/?tab=readme-ov-file#provided-subtemplates).
See also the documentation of [Mockup and Patternslib](https://6.docs.plone.org/classic-ui/mockup.html) for how to build the UI toolkit for Classic UI.
```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
