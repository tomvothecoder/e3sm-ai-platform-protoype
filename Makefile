VENV := .venv
PYTHON := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff

.PHONY: help venv install activate corpus-sync test run lint format

help:
	@printf '%s\n' \
		'make venv      Create the uv virtual environment' \
		'make install   Install requirements into the environment' \
		'make activate  Open an interactive shell in the environment' \
		'make corpus-sync  Download the pinned E3SM corpus' \
		'make test      Run unit tests' \
		'make run       Run the LlamaIndex starter' \
		'make lint      Check Python code with Ruff' \
		'make format    Format Python code with Ruff'

venv: $(PYTHON)

$(PYTHON):
	uv venv $(VENV)

install: venv
	uv pip install --python $(PYTHON) -r requirements.txt

activate: venv
	@printf '%s\n' 'Opening activated shell; exit it to return.'
	@. $(VENV)/bin/activate && exec "$${SHELL:-/bin/sh}" -i

corpus-sync:
	$(PYTHON) -m scripts.sync_corpus

test:
	$(PYTHON) -m unittest discover -s tests

run:
	$(PYTHON) -m app.starter

lint:
	$(RUFF) check .

format:
	$(RUFF) format .
