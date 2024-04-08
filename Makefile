all: help

.PHONY: help
help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#
# https://makefiletutorial.com
#
SHELL         := /bin/bash
GIT           := git

VERSION       = $(shell $(GIT) describe --always --tags --match "[0-9\.]*")
NEXT_VERSION  = $(shell $(GIT) describe --always --tags --match "[0-9\.]*" --abbrev=0 | awk -F. '{OFS="."; $$NF+=1; print $$0}')

.PHONY: tag-release
tag-release: ## Create new git tag for the next version
	$(GIT) tag -a -m "Release $(NEXT_VERSION)" $(NEXT_VERSION)
	$(GIT) push origin $(NEXT_VERSION)

.PHONY: show-version
show-version: ## Show current and next version
	@echo "current version: $(VERSION)"
	@echo "next version: $(NEXT_VERSION)"


PN := hse_cv_project

SHELL  := /bin/sh

SYSTEM_PYTHON := $(shell which python3)
PYTHON        := venv/bin/python
PIP           := $(PYTHON) -m pip
MYPY          := $(PYTHON) -m mypy
PYTEST        := $(PYTHON) -m pytest

LINT_TARGET := src/ tests/
MYPY_TARGET := src/${PN} tests/


venv: ## Create venv
	$(SYSTEM_PYTHON) -m venv venv
	$(PIP) install --upgrade pip wheel


.PHONY: run
# target: clean - Remove intermediate and generated files
run:
	@${PYTHON} src/hse_cv_project/demo.py -w share/model_float16_quant.tflite

.PHONY: clean
# target: clean - Remove intermediate and generated files
clean:
	@find . -type f -name '*.py[co]' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -rf {build,htmlcov,cover,coverage,dist,.coverage,.hypothesis}
	@rm -rf src/*.egg-info
	@rm -f VERSION


.PHONY: develop
# target: develop - Install package in editable mode with `develop` extras
develop:
	@${PYTHON} -m pip install --upgrade pip setuptools wheel
	@${PYTHON} -m pip install -e .[develop]




.PHONY: distcheck-clean
distcheck-clean:
	@rm -rf dist/$(PN)

.PHONY: format
# target: format - Format the code according to the coding styles
format: format-black format-isort format-ruff


.PHONY: format-black
format-black:
	@black ${LINT_TARGET}


.PHONY: format-isort
format-isort:
	@isort ${LINT_TARGET}

.PHONY: format-ruff
format-ruff:
	@ruff format ${LINT_TARGET}


.PHONY: lint
# target: lint - Check source code with linters
lint: lint-isort lint-black lint-mypy lint-ruff


.PHONY: lint-black
lint-black:
	@${PYTHON} -m black --check --diff ${LINT_TARGET}


.PHONY: lint-isort
lint-isort:
	@${PYTHON} -m isort.main -c  ${LINT_TARGET}


.PHONY: lint-mypy
lint-mypy:
	@${MYPY} ${MYPY_TARGET}


.PHONY: lint-ruff
lint-ruff:
	@${PYTHON} -m ruff check ${LINT_TARGET}


.PHONY: purge
# target: purge - Remove all unversioned files and reset working copy
purge:
	@git reset --hard HEAD
	@git clean -xdff


.PHONY: report-coverage
# target: report-coverage - Print coverage report
report-coverage:
	@${PYTHON} -m coverage report

.PHONY: test
# target: test - Run tests
test:
	@${PYTEST} -s -v tests

.PHONY: install
# target: install - Install the project
install:
	@pip install .


.PHONY: uninstall
# target: uninstall - Uninstall the project
uninstall:
	@pip uninstall $(PN)

