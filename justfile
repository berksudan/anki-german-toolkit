set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

PYTHON_VERSION := "3.14"
VENV_DIR := justfile_directory() / ".venv"

default:
    @just --list

setup:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf "{{ VENV_DIR }}"
    uv venv "{{ VENV_DIR }}" --python "{{ PYTHON_VERSION }}"
    echo "export PYTHONPATH={{ justfile_directory() }}/" >> "{{ VENV_DIR }}/bin/activate"
    uv sync --locked
    "{{ VENV_DIR }}/bin/prek" install
    echo "Activate the virtual environment: source {{ VENV_DIR }}/bin/activate"

duden word:
    @uv run duden "$1"

cards-list:
    @uv run python -m scripts.suggest_anki_cards_cli list

cards-lookup *words:
    @uv run --env-file .env python -m scripts.suggest_anki_cards_cli lookup "$@"

cards-build json:
    @uv run python -m scripts.suggest_anki_cards_cli build "$1"
