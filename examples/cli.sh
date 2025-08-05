#!/bin/bash

export PYTHONPATH=$(pwd)
ARGS="$@"

 
uv run python3 -m g4f.cli $ARGS