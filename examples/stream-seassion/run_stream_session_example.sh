#!/bin/bash

 
# Mengatur variabel lingkungan
# export PYTHONPATH=$(pwd)
export PYTHONPATH=$(pwd):$(pwd)/.deps/gpt4free

# export G4F_PROXY="socks5://127.0.0.1:1083"

# Menampilkan informasi
echo "Mengatur PYTHONPATH ke: $(pwd)" 
echo "Menjalankan contoh StreamSession..."
uv run python examples/stream-seassion/extended_glm_stream.py 