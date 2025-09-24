#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/.deps/gpt4free

 
uv run python examples/custom_inference_api/init_database.py
