---
myst:
  html_meta:
    "description": "Run collective.polls and its Volto add-on from the repository, with example content."
    "property=og:description": "Run collective.polls and its Volto add-on from the repository, with example content."
    "property=og:title": "Run the development environment"
    "keywords": "Plone, Volto, polls, development, make"
---

(install-development)=

# Run the development environment

The repository holds both add-ons and everything needed to run them together, with example content that includes polls.
Use it to try the add-ons, or to work on them.

## Requirements

-   [uv](https://docs.astral.sh/uv/)
-   [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
-   [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 24
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)

## Run it

1.  Clone the repository, and install it.

    ```shell
    git clone https://github.com/collective/collective.polls.git
    cd collective.polls
    make install
    ```

2.  Create a Plone site with the example content.
    This replaces any site created before.

    ```shell
    make backend-create-site
    ```

3.  Start the backend at http://localhost:8080/.

    ```shell
    make backend-start
    ```

4.  In a second shell session, start the frontend at http://localhost:3000/.

    ```shell
    make frontend-start
    ```

Log in with the user `admin` and the password `admin`.

## Next steps

-   {doc}`/tutorials/first-poll`: run a poll from start to finish in this site.
