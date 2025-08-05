#!/bin/bash

export PYTHONPATH=$(pwd)

uv run python3 -m examples.custom_inference_api.web_interface
