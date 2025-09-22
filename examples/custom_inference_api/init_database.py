#!/usr/bin/env python3
"""
Script untuk menginisialisasi database
"""

# Import semua model agar terdaftar di Base
from examples.custom_inference_api.db.db_connection import Base, engine
from examples.custom_inference_api.db.models import (
    Participant, Folder, Conversation, Message, 
    User, MessageGroup, Attachment, Session, Usage
)

def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada"""
    # Membuat semua tabel
    Base.metadata.create_all(bind=engine)
    print("Database berhasil diinisialisasi!")

if __name__ == "__main__":
    init_db()