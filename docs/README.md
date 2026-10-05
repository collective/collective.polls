# collective.polls documentation

The sources of the [collective.polls documentation](https://collective.github.io/collective.polls/).

It is built with Sphinx and the [Plone Sphinx Theme](https://github.com/plone/plone-sphinx-theme), and organized following [Diátaxis](https://diataxis.fr/).
The `collective.polls` backend package is installed into the documentation environment, from `../backend/`, so the documentation shows the version of the code beside it.

## Prerequisites

-   [uv](https://docs.astral.sh/uv/) manages the Python version and the dependencies.

To install uv, use the following command, or visit the [uv installation page](https://docs.astral.sh/uv/getting-started/installation/) for alternative methods.

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Build documentation

From the root of the repository, install the documentation toolchain, then build the documentation the way CI does, with warnings as errors.

```shell
make docs-install
make docs-build
```

The remaining commands run inside this `docs` folder.

To build the HTML documentation and view a live preview while editing, issue the following command.

```shell
make livehtml
```

To check for broken links, issue the following command.

```shell
make linkcheckbroken
```

To check spelling, grammar, and style, issue the following command.
You should pay attention to errors and warnings, and suggestions may get noisy.

```shell
make vale
```

To delete the build directory and the Python virtual environment, and reinitialize the environment, issue the following command.
This is useful to force reinstalling dependencies and purging cached files in Sphinx builds.

```shell
make init
```

For more `make` commands, issue the following command.

```shell
make help
```

## Customize the documentation

The file `docs/conf.py` controls the configuration of the documentation.
It has extensive comments for each part, often with links to the authoritative documentation for extensions and configuration.

### Manage dependencies

The documentation's requirements are in the `dev` dependency group of `pyproject.toml`.

To add a requirement, use the following command.

```shell
uv add --dev my-requirement
```

To remove a requirement, use the following command.

```shell
uv remove --dev my-requirement
```

After adding a Sphinx extension, also add it to the `extensions` key of `conf.py`.
See also uv's documentation, [Development dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies).

### Capture the screenshots

The screenshots are captured from the development site's example content by Playwright scripts.
See `screenshots/README.md`, then issue the following commands with the site running.

```shell
make screenshots-install
make screenshots
```

### Replace static files

The logo and the favicon are `docs/_static/logo.svg` and `docs/_static/favicon.ico`.
The favicon is built from the logo; after changing `logo.svg`, rebuild it with the following command, which needs `rsvg-convert` from [librsvg](https://gitlab.gnome.org/GNOME/librsvg).

```shell
make favicon
```

If you rename `logo.svg`, update the `html_logo`, `ogp_image`, and `latex_logo` keys in `conf.py`.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
