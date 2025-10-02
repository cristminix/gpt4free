#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/.deps/gpt4free

export G4F_PROXY="" #http://127.0.0.1:8081"

# uv run python -m examples.custom_inference_api.web_interface --debug
uv run uvicorn examples.solids.extended.run_custom_gui:app --host 0.0.0.0 --port 7000 --reload
