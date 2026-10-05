### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
UV?=uv

# installed?
ifeq (, $(shell which $(UV) ))
  $(error "UV=$(UV) not found in $(PATH)")
endif

REPOSITORY_SETTINGS := $(shell uvx repoplone settings dump)
IMAGE_NAME_PREFIX := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.container_images_prefix')
IMAGE_NAME_SEPARATOR := -
IMAGE_NAME_PREFIX_WITH_SEPARATOR := $(IMAGE_NAME_PREFIX)$(IMAGE_NAME_SEPARATOR)

IMAGE_TAG=latest
IMAGE_NAME=$(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend:$(IMAGE_TAG)

PLONE_SITE_ID=Plone
BACKEND_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
EXAMPLE_CONTENT_FOLDER := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.backend.code_path')/setuphandlers/examplecontent
PACKAGE_NAME := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.backend.name')

VENV_FOLDER=$(BACKEND_FOLDER)/.venv
export VIRTUAL_ENV=$(VENV_FOLDER)
BIN_FOLDER=$(VENV_FOLDER)/bin

# Environment variables to be exported
export PYTHONWARNINGS := ignore
export DOCKER_BUILDKIT := 1
export PYTHON_VERSION := 3.11
export PLONE_VERSION := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.backend.base_package_version')

ifdef CI
UV_VENV_ARGS :=
else
UV_VENV_ARGS := --python=$(PYTHON_VERSION)
endif


all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: debug-settings
debug-settings:  ## Debug settings
	@echo "PLONE_VERSION: $(PLONE_VERSION)"
	@echo "PACKAGE_NAME: $(PACKAGE_NAME)"
	@echo "EXAMPLE_CONTENT_FOLDER: $(EXAMPLE_CONTENT_FOLDER)"
	@echo "IMAGE_NAME_PREFIX_WITH_SEPARATOR: $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)"
	@echo "IMAGE_NAME: $(IMAGE_NAME)"


requirements-mxdev.txt: pyproject.toml mx.ini ## Generate constraints file
	@echo "$(GREEN)==> Generate constraints file$(RESET)"
	@echo '-c https://dist.plone.org/release/$(PLONE_VERSION)/constraints.txt' > requirements.txt
	@uvx 'mxdev[uv]' -c mx.ini

$(VENV_FOLDER): requirements-mxdev.txt ## Install dependencies
	@echo "$(GREEN)==> Install environment$(RESET)"
	@if [[ -d "$(VENV_FOLDER)" ]]; then echo "$(YELLOW)==> Environment already exists at $(VENV_FOLDER)$(RESET)"; else uv venv $(UV_VENV_ARGS) $(VENV_FOLDER); fi
	@uv pip install -r requirements-mxdev.txt

.PHONY: sync
sync: $(VENV_FOLDER) ## Sync project dependencies
	@echo "$(GREEN)==> Sync project dependencies$(RESET)"
	@uv pip install -r requirements-mxdev.txt

instance/etc/zope.ini instance/etc/zope.conf: instance.yaml ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	@uvx cookiecutter -f --no-input -c 3.1.0 --config-file instance.yaml gh:plone/cookiecutter-zope-instance

.PHONY: config
config: instance/etc/zope.ini

.PHONY: install
install: $(VENV_FOLDER) config ## Install Plone and dependencies

.PHONY: clean
clean: ## Clean installation and instance
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	@rm -rf $(VENV_FOLDER) pyvenv.cfg .installed.cfg instance/etc .venv .pytest_cache .ruff_cache constraints* requirements*

.PHONY: remove-data
remove-data: ## Remove all content
	@echo "$(RED)==> Removing all content$(RESET)"
	rm -rf $(VENV_FOLDER) instance/var

.PHONY: start
start: $(VENV_FOLDER) instance/etc/zope.ini ## Start a Plone instance on localhost:8080
	@$(BIN_FOLDER)/runwsgi instance/etc/zope.ini

.PHONY: console
console: $(VENV_FOLDER) instance/etc/zope.ini ## Start a console into a Plone instance
	@$(BIN_FOLDER)/zconsole debug instance/etc/zope.conf

.PHONY: create-site
create-site: $(VENV_FOLDER) instance/etc/zope.ini ## Create a new site from scratch
	@$(BIN_FOLDER)/zconsole run instance/etc/zope.conf ./scripts/create_site.py

# Example Content
.PHONY: update-example-content
update-example-content: $(VENV_FOLDER) ## Export example content inside package
	@echo "$(GREEN)==> Export example content into $(EXAMPLE_CONTENT_FOLDER) $(RESET)"
	if [ -d $(EXAMPLE_CONTENT_FOLDER)/content ]; then rm -r $(EXAMPLE_CONTENT_FOLDER)/* ;fi
	@$(BIN_FOLDER)/plone-exporter instance/etc/zope.conf $(PLONE_SITE_ID) $(EXAMPLE_CONTENT_FOLDER)

# QA
.PHONY: lint
lint: ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Lint codebase$(RESET)"
	@uvx ruff@latest check --fix --config $(BACKEND_FOLDER)/pyproject.toml
	@uvx pyroma@latest -d .
	@uvx check-python-versions@latest .
	@uvx zpretty@latest --check src

.PHONY: format
format: ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	@uvx ruff@latest check --select I --fix --config $(BACKEND_FOLDER)/pyproject.toml
	@uvx ruff@latest format --config $(BACKEND_FOLDER)/pyproject.toml
	@uvx zpretty@latest -i src

# i18n
.PHONY: i18n
i18n: $(VENV_FOLDER) ## Update locales
	@echo "$(GREEN)==> Updating locales$(RESET)"
	@$(BIN_FOLDER)/python -m $(PACKAGE_NAME).locales

# Tests
.PHONY: test
test: $(VENV_FOLDER) ## run tests
	@$(BIN_FOLDER)/pytest

.PHONY: test-coverage
test-coverage: $(VENV_FOLDER) ## run tests with coverage
	@$(BIN_FOLDER)/pytest --cov=$(PACKAGE_NAME) --cov-report term-missing

# Build Docker images
.PHONY: build-image
build-image:  ## Build Docker Images
	@docker build . -t $(IMAGE_NAME) -f Dockerfile --build-arg PLONE_VERSION=$(PLONE_VERSION)

# Acceptance tests
.PHONY: acceptance-backend-start
acceptance-backend-start: ## Start backend acceptance server
	ZSERVER_HOST=0.0.0.0 ZSERVER_PORT=55001 LISTEN_PORT=55001 APPLY_PROFILES="$(PACKAGE_NAME):default" CONFIGURE_PACKAGES="plone.restapi,plone.volto,plone.volto.cors,$(PACKAGE_NAME)" $(BIN_FOLDER)/robot-server plone.app.robotframework.testing.VOLTO_ROBOT_TESTING

.PHONY: acceptance-image-build
acceptance-image-build:  ## Build Docker Images
	@docker build . -t $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend-acceptance:$(IMAGE_TAG) -f Dockerfile.acceptance --build-arg PLONE_VERSION=$(PLONE_VERSION)

## Add bobtemplates features (check bobtemplates.plone's documentation to get the list of available features)
add: $(VENV_FOLDER)
	@uvx plonecli add $(filter-out $@,$(MAKECMDGOALS))
