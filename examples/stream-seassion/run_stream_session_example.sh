#!/bin/bash

# Script untuk menjalankan contoh StreamSession

# Mengatur variabel lingkungan
export PYTHONPATH=$(pwd)
export G4F_PROXY="socks5://127.0.0.1:1083"

# Menampilkan informasi
echo "Mengatur PYTHONPATH ke: $(pwd)"
echo "Mengatur G4F_PROXY ke: $G4F_PROXY"

# Menjalankan contoh StreamSession
echo "Menjalankan contoh StreamSession..."
uv run python3 examples/stream-seassion/simple_stream_session_example.py
uv run python3 examples/stream-seassion/stream_session_example.py

# Memeriksa status keluar
if [ $? -eq 0 ]; then
    echo "Contoh StreamSession berhasil dijalankan."
else
    echo "Terjadi kesalahan saat menjalankan contoh StreamSession."
    exit 1
fi