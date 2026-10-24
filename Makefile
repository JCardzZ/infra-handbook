# Uses the project virtualenv (.venv) without needing to activate it.
VENV ?= .venv
MKDOCS := $(VENV)/bin/mkdocs
# For scripts/build-diagrams.sh, which calls python3.
export PATH := $(CURDIR)/$(VENV)/bin:$(PATH)

.PHONY: serve diagrams build

serve: ## Run the site locally with live reload
	$(MKDOCS) serve

diagrams: ## Render diagrams/*.py to SVG in docs/assets/diagrams/
	./scripts/build-diagrams.sh

build: diagrams ## Render diagrams, then build the site with zero warnings allowed
	$(MKDOCS) build --strict
