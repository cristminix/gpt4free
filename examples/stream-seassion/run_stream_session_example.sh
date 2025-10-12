#!/bin/bash

 
# Mengatur variabel lingkungan
# export PYTHONPATH=$(pwd)
export PYTHONPATH=$(pwd):$(pwd)/.deps/gpt4free

export G4F_PROXY="http://127.0.0.1:8081"

# Menampilkan informasi
echo "Mengatur PYTHONPATH ke: $(pwd)" 
echo "Menjalankan contoh StreamSession..."
# uv run python examples/stream-seassion/extended_glm_stream.py 
# uv run python examples/stream-seassion/extended_lmarena_beta_stream.py 
uv run python examples/stream-seassion/factory_stream.py 