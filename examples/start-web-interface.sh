#!/bin/bash

export PYTHONPATH=$(pwd)
export G4F_PROXY="socks5://127.0.0.1:1083"

uv run python3 -m examples.custom_inference_api.web_interface --debug
