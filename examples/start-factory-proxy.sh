#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/.deps/gpt4free
#export G4F_PROXY="http://127.0.0.1:8081"
# uv run python3 -m examples.custom_inference_api.run --debug
uv run uvicorn examples.factory_transparent_proxy:create_transparent_proxy --host 0.0.0.0 --port 7777 --reload
