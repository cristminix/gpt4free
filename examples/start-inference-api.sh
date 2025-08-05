#!/bin/bash

export PYTHONPATH=$(pwd)
export HUGGINGFACE_API_KEY=""
export TOGETHER_API_KEY=""
export OPENAI_API_KEY="..-hjcE"

uv run python3 -m examples.custom_inference_api.run