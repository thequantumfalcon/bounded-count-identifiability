PYTHON ?= python
.DEFAULT_GOAL := help
.PHONY: help setup lint test fuzz build artifacts formal release

help setup lint test fuzz build artifacts formal release:
	$(PYTHON) tools/tasks.py $@
