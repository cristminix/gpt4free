#!/usr/bin/env python3
"""
Script untuk menginisialisasi database menggunakan pendekatan langsung dengan SQLAlchemy
"""

import os
import sys

# Tambahkan direktori saat ini ke path Python
sys.path.insert(0, '/home/cristminix/projects/gpt4free')

# Import semua model agar terdaftar di Base
from examples.custom_inference_api.db.db_connection import Base, engine
from examples.custom_inference_api.db.models import (
    Participant, Folder, Conversation, Message, 
    User, MessageGroup, Attachment, Session, Usage
)

def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada"""
    # Pastikan direktori database ada
    db_path = "examples/gpt4free.db"
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Membuat semua tabel
    Base.metadata.create_all(bind=engine)
    print("Database berhasil diinisialisasi!")

if __name__ == "__main__":
    init_db()