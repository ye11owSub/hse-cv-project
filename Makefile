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


PN := hse-cv-project
PV := `python setup.py -q --version`

SHELL  := /bin/sh

SYSTEM_PYTHON := $(shell which python3)
PYTHON        := venv/bin/python
PIP           := $(PYTHON) -m pip
MYPY          := $(PYTHON) -m mypy
FLAKE8        := $(PYTHON) -m flake8
PYTEST        := $(PYTHON) -m pytest

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
	@${PYTHON} setup.py clean
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


.PHONY: dist
# target: dist - Build all artifacts
dist: dist-sdist dist-wheel dist-egg


.PHONY: dist-sdist
# target: dist-sdist - Build sdist artifact
dist-sdist:
	@${PYTHON} setup.py sdist


.PHONY: dist-wheel
# target: dist-wheel - Build wheel artifact
dist-wheel:
	@${PYTHON} setup.py bdist_wheel


.PHONY: dist-egg
# target: dist-egg - Build egg artifact
dist-egg:
	@rm dist/*.egg share/dmp/*.egg || echo "No eggs to remove"
	@${PYTHON} setup.py bdist_egg
	@cp dist/*.egg share/dmp/


.PHONY: distcheck
# target: distcheck - Verify distributed artifacts
distcheck: distcheck-clean sdist
	@mkdir -p dist/$(PN)
	@tar -xf dist/$(PN)-$(PV).tar.gz -C dist/$(PN) --strip-components=1
	@$(MAKE) -C dist/$(PN) venv
	. dist/$(PN)/venv/bin/activate && $(MAKE) -C dist/$(PN) develop
	. dist/$(PN)/venv/bin/activate && $(MAKE) -C dist/$(PN) check
	@rm -rf dist/$(PN)


.PHONY: distcheck-clean
distcheck-clean:
	@rm -rf dist/$(PN)


.PHONY: install
# target: install - Install the project
install:
	@pip install .


.PHONY: uninstall
# target: uninstall - Uninstall the project
uninstall:
	@pip uninstall $(PN)

