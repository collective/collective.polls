### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
GIT_FOLDER=$(CURRENT_DIR)/.git

REPOSITORY_SETTINGS := $(shell uvx repoplone settings dump)

PROJECT_NAME=$(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.name')
STACK_NAME=${PROJECT_NAME}

IMAGE_NAME_PREFIX := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.container_images_prefix')
IMAGE_NAME_SEPARATOR := -
IMAGE_NAME_PREFIX_WITH_SEPARATOR := $(IMAGE_NAME_PREFIX)$(IMAGE_NAME_SEPARATOR)

# Environment variables to be exported
export VOLTO_VERSION := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.frontend.volto_version')
export PLONE_VERSION := $(shell echo '$(REPOSITORY_SETTINGS)' | jq -r '.backend.base_package_version')

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

.PHONY: all
all: install

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: debug-settings
debug-settings:  ## Debug settings
	@echo "Debug settings"
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "VOLTO_VERSION: $(VOLTO_VERSION)"
	@echo "PLONE_VERSION: $(PLONE_VERSION)"
	@echo "IMAGE_NAME_PREFIX: $(IMAGE_NAME_PREFIX)"
	@echo "IMAGE_NAME_PREFIX_WITH_SEPARATOR: $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)"

###########################################
# Frontend
###########################################
.PHONY: frontend-install
frontend-install:  ## Install React Frontend
	$(MAKE) -C "./frontend/" install

.PHONY: frontend-build
frontend-build:  ## Build React Frontend
	$(MAKE) -C "./frontend/" build

.PHONY: frontend-start
frontend-start:  ## Start React Frontend
	$(MAKE) -C "./frontend/" start

.PHONY: frontend-test
frontend-test:  ## Test frontend codebase
	@echo "Test frontend"
	$(MAKE) -C "./frontend/" test

###########################################
# Backend
###########################################
.PHONY: backend-install
backend-install:  ## Create virtualenv and install Plone
	$(MAKE) -C "./backend/" install
	$(MAKE) backend-create-site

.PHONY: backend-build
backend-build:  ## Build Backend
	$(MAKE) -C "./backend/" install

.PHONY: backend-create-site
backend-create-site: ## Create a Plone site with default content
	$(MAKE) -C "./backend/" create-site

.PHONY: backend-update-example-content
backend-update-example-content: ## Export example content inside package
	$(MAKE) -C "./backend/" update-example-content

.PHONY: backend-start
backend-start: ## Start Plone Backend
	$(MAKE) -C "./backend/" start

.PHONY: backend-test
backend-test:  ## Test backend codebase
	@echo "Test backend"
	$(MAKE) -C "./backend/" test

###########################################
# Environment
###########################################
.PHONY: install
install:  ## Install
	@echo "Install Backend & Frontend"
	$(MAKE) backend-install
	$(MAKE) frontend-install

.PHONY: clean
clean:  ## Clean installation
	@echo "Clean installation"
	$(MAKE) -C "./backend/" clean
	$(MAKE) -C "./frontend/" clean

###########################################
# QA
###########################################
.PHONY: format
format:  ## Format codebase
	@echo "Format the codebase"
	$(MAKE) -C "./backend/" format
	$(MAKE) -C "./frontend/" format

.PHONY: lint
lint:  ## Format codebase
	@echo "Lint the codebase"
	$(MAKE) -C "./backend/" lint
	$(MAKE) -C "./frontend/" lint

.PHONY: check
check:  format lint ## Lint and Format codebase

###########################################
# i18n
###########################################
.PHONY: i18n
i18n:  ## Update locales
	@echo "Update locales"
	$(MAKE) -C "./backend/" i18n
	$(MAKE) -C "./frontend/" i18n

###########################################
# Testing
###########################################
.PHONY: test
test:  backend-test frontend-test ## Test codebase

###########################################
# Container images
###########################################
.PHONY: build-images
build-images:  ## Build container images
	@echo "Build"
	$(MAKE) -C "./backend/" build-image
	$(MAKE) -C "./frontend/" build-image

###########################################
# Local Stack
###########################################
.PHONY: stack-create-site
stack-create-site:  ## Local Stack: Create a new site
	@echo "Create a new site in the local Docker stack"
	@echo "(Stack must not be running already.)"
	@docker compose -f docker-compose.yml run --build backend ./docker-entrypoint.sh create-site

.PHONY: stack-start
stack-start:  ## Local Stack: Start Services
	@echo "Start local Docker stack"
	@docker compose -f docker-compose.yml up -d --build
	@echo "Now visit: http://$(PROJECT_NAME).localhost"

.PHONY: stack-status
stack-status:  ## Local Stack: Check Status
	@echo "Check the status of the local Docker stack"
	@docker compose -f docker-compose.yml ps

.PHONY: stack-stop
stack-stop:  ##  Local Stack: Stop Services
	@echo "Stop local Docker stack"
	@docker compose -f docker-compose.yml stop

.PHONY: stack-rm
stack-rm:  ## Local Stack: Remove Services and Volumes
	@echo "Remove local Docker stack"
	@docker compose -f docker-compose.yml down
	@echo "Remove local volume data"
	@docker volume rm $(PROJECT_NAME)_vol-site-data

###########################################
# Acceptance
###########################################
.PHONY: acceptance-backend-start
acceptance-backend-start:
	@echo "Start acceptance backend"
	$(MAKE) -C "./backend/" acceptance-backend-start

.PHONY: acceptance-frontend-dev-start
acceptance-frontend-dev-start:
	@echo "Start acceptance frontend"
	$(MAKE) -C "./frontend/" acceptance-frontend-dev-start

.PHONY: acceptance-test
acceptance-test:
	@echo "Start acceptance tests in interactive mode"
	$(MAKE) -C "./frontend/" acceptance-test

# Build Docker images
.PHONY: acceptance-frontend-image-build
acceptance-frontend-image-build:
	@echo "Build acceptance frontend image"
	@docker build frontend -t $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)frontend:acceptance -f frontend/Dockerfile --build-arg VOLTO_VERSION=$(VOLTO_VERSION)

.PHONY: acceptance-backend-image-build
acceptance-backend-image-build:
	@echo "Build acceptance backend image"
	@docker build backend -t $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend:acceptance -f backend/Dockerfile.acceptance --build-arg PLONE_VERSION=$(PLONE_VERSION)

.PHONY: acceptance-images-build
acceptance-images-build: ## Build Acceptance frontend/backend images
	$(MAKE) acceptance-backend-image-build
	$(MAKE) acceptance-frontend-image-build

.PHONY: acceptance-frontend-container-start
acceptance-frontend-container-start:
	@echo "Start acceptance frontend"
	@docker run --rm -p 3000:3000 --name $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)frontend-acceptance --link $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend-acceptance:backend -e RAZZLE_API_PATH=http://localhost:55001/plone -e RAZZLE_INTERNAL_API_PATH=http://backend:55001/plone -d $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)frontend:acceptance

.PHONY: acceptance-backend-container-start
acceptance-backend-container-start:
	@echo "Start acceptance backend"
	@docker run --rm -p 55001:55001 --name $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend-acceptance -d $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend:acceptance

.PHONY: acceptance-containers-start
acceptance-containers-start: ## Start Acceptance containers
	$(MAKE) acceptance-backend-container-start
	$(MAKE) acceptance-frontend-container-start

.PHONY: acceptance-containers-stop
acceptance-containers-stop: ## Stop Acceptance containers
	@echo "Stop acceptance containers"
	@docker stop $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)frontend-acceptance
	@docker stop $(IMAGE_NAME_PREFIX_WITH_SEPARATOR)backend-acceptance

.PHONY: ci-acceptance-test
ci-acceptance-test:
	@echo "Run acceptance tests in CI mode"
	$(MAKE) acceptance-containers-start
	pnpm dlx wait-on --httpTimeout 20000 http-get://localhost:55001/plone http://localhost:3000
	$(MAKE) -C "./frontend/" ci-acceptance-test
	$(MAKE) acceptance-containers-stop
