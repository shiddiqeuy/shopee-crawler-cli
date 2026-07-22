#!/usr/bin/env bash

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

if [ $# -eq 0 ]; then
    python3 run.py menu
else
    python3 run.py "$@"
fi
