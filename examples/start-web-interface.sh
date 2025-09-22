#!/bin/bash

export PYTHONPATH=$(pwd)
export G4F_PROXY="http://127.0.0.1:8081"

uv run python3 -m examples.custom_inference_api.web_interface --debug
