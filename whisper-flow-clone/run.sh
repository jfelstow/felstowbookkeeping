#!/usr/bin/env bash
# One-command setup + launch. First run creates a virtualenv and installs
# dependencies; after that it starts instantly. Any arguments are passed
# through to dictate.py (e.g. ./run.sh --model small.en --toggle).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "First run: setting up (takes a minute)..."
    python3 -m venv .venv
    ./.venv/bin/pip install --quiet --upgrade pip
    ./.venv/bin/pip install --quiet -r requirements.txt
fi

exec ./.venv/bin/python dictate.py "$@"
