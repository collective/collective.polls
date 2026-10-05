---
name: "Instructions: Plone addon monorepo documentation"
description: "Standards and guidelines for documentation files for Plone addons with backend and frontend components"
applyTo: "README.md,docs/docs/**/*.md,docs/README.md,backend/README.md,frontend/README.md"
---

# Plone addon documentation standards

This document outlines the standards and guidelines for documentation files in a repository for a Plone addon that will release a backend (Pypi) and a frontend (NPM) package.

## 0. General guidelines

Always read the general rules for Plone documentation in ./general/docs.md

## 1. All files

- ALWAYS use emojis in section titles for a friendly tone.
- ALWAYS recommend using `make` commands for installation and starting the project:
    - ALWAYS recommend using `make install` to install the project and its components, as this handles all dependencies and setup.
    - ALWAYS recommend using `make start` to start processes, as this ensures proper configuration.
- NEVER recomend using `pnpm install` or `pnpm start` directly.
- NEVER recomend using `pip install`, `uv add`  or `uv pip` directly.
- NEVER edit the paragraph refering to `cookieplone`. Usually starting with **Generated using**.

## 2. README.md at the top level of the repository

- Must provide a clear overview of both frontend and backend parts of the addon
- Will be viewed on GitHub
- Must provide installation for developers willing to contribute to this add-on.
- Must point to installation instructions for end users available in the frontend and backend README files.
- Must refer to the backend and frontend addons.
- Must describe the features.
    - Example:
        - ✅: `- Register a behavior providing additiional fields representing contact information` .
        - ❌: `- Behavior` .
    - Review the code if necessary to explain it.


## 3. backend/README.md

- Must provide a clear overview of the addon
- Will be viewed on PyPI
- Must provide installation instructions for end users.
- Must link to the top-level README of the repository for developers willing to contribute to this add-on.
- Must describe the features.
    - Example:
        - ✅: `- Register a behavior providing additiional fields representing contact information` .
        - ❌: `- Behavior` .
    - Review the code if necessary to explain it.

## 4. frontend/README.md

- Must provide a clear overview of the addon
- Will be viewed on NPM
- Must provide installation instructions for end users.
- Must link to the top-level README of the repository for developers willing to contribute to this add-on.
- Must describe the features.
    - Example:
        - ✅: `- Crops the image. Supports many aspect ratios` .
        - ❌: `- Crop` .
    - Review the code if necessary to explain it.
- ADDING THIS ADD-ON TO YOUR PROJECT:
    - NEVER recommend editing the top-level `package.json` manually
    - ALWAYS recommend editing the 'policy package' `package.json` instead.
    - THIS 'policy package' will always be available under `packages` folder.
    - ALWAYS recommend adding this add-on to the "addons" array in package.json

## 5. docs/README.md
- Must provide detailed documentation for developers **documenting** the project
