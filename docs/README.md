# Polls for Plone

Documentation for Polls for Plone.
Online polls support for Plone and Volto.

This project provides a Sphinx-based documentation environment for your Plone project, powered by the [Plone Sphinx Theme](https://github.com/plone/plone-sphinx-theme).
It's generated using the `documentation_starter` template from [Cookieplone](https://github.com/plone/cookieplone).


## Prerequisites

-   [uv](https://docs.astral.sh/uv/) is the recommended tool for managing Python versions and project dependencies.

To install uv, use the following command, or visit the [uv installation page](https://docs.astral.sh/uv/getting-started/installation/) for alternative methods.

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```


## Build documentation

To build the HTML documentation, issue the following command.

```shell
make html
```

To build the HTML documentation and view a live preview while editing your documentation, issue the following command.

```shell
make livehtml
```

To check for broken links in your documentation, issue the following command.

```shell
make linkcheckbroken
```

To check spelling, grammar, and style in your documentation, issue the following command.
You should pay attention to errors and warnings, and suggestions may get noisy.

```shell
make vale
```

To delete the `docs` build directory and Python virtual environment, and reinitialize Python virtual environment, issue the following command.
This is useful to force reinstall dependencies and purge cached files in Sphinx builds.

```shell
make init
```

For more `make` commands, issue the following command.

```shell
make help
```


## Customize the Polls for Plone documentation

This section provides how-to guidance to customize your documentation.

The file `docs/conf.py` controls the configuration of your documentation.
It has extensive comments for each part, often with links to the authoritative documentation for extensions and configuration.

The following sections describe customization not addressed in `docs/conf.py`.


### Manage dependencies

You can configure which dependencies or requirements you want to use in your documentation using uv.
Requirements are stored in the `dev` dependency group in the `pyproject.toml` file.

To add a requirement, use the following command.

```shell
uv add --dev my-requirement
```

To remove a requirement, use the following command.

```shell
uv remove --dev my-requirement
```

See also uv's documentation [Development dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies).

After installing a dependency, you might need to add it to your documentation's configuration file, `conf.py`, under the `extensions` key.


### Replace static files

You might want to replace the default static files, located in `docs/_static`, `logo.svg` and `favicon.ico`.
Plone Sphinx Theme is configured to use these files when rendering documentation to HTML.

If you rename `logo.svg`, you must update `conf.py`, under the `html_logo`, `ogp_image`, and `latex_logo` keys.


## Read the Docs

Now that you've built your documentation, how do you publish it?
And how do you get collaborators to easily review your changes to your documentation?

Thankfully, [Read the Docs](https://about.readthedocs.com/) provides both hosting of documentation and pull request previews.
For public repositories, this service is free.
However, the Plone Foundation donates to Read the Docs for their unwavering support to open source software, and encourages you to do the same.

Your documentation scaffold is partially configured to use Read the Docs.
In several files, search for the string `MY_READTHEDOCS_PROJECT_SLUG`.
You'll need to replace that string with the slug that Read the Docs creates for you when you import your project.

For complete documentation of this process, see the Plone 6 Documentation [Pull request preview builds](https://6.docs.plone.org/contributing/documentation/admins.html#pull-request-preview-builds).

See also Read the Docs documentation:

-   [Pull request previews](https://docs.readthedocs.com/platform/stable/pull-requests.html)
-   [Build process overview](https://docs.readthedocs.com/platform/stable/builds.html)

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (99c2201)](https://github.com/plone/cookieplone-templates/commit/99c2201962371b182499a0d71f45ed878da0c33d) on 2026-10-04 22:40:50.366931. A special thanks to all contributors and supporters!
