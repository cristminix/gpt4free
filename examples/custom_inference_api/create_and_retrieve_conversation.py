#!/usr/bin/env python3
"""
Script untuk membuat percakapan dan mengambil percakapan dari database
"""

import sys
import os
import uuid
from datetime import datetime

# Tambahkan direktori proyek ke path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from examples.custom_inference_api.db.db_connection import init_db, base_db
from examples.custom_inference_api.db.models import Conversation

def create_conversation(title, system_message="", user_id=1, enable_system_message=1, folder_id=None):
    """Membuat percakapan baru dalam database"""
    try:
        # Inisialisasi database jika belum diinisialisasi
        init_db()
        
        # Membuat data percakapan
        conversation_data = {
            'id': str(uuid.uuid4()),
            'title': title,
            'system_message': system_message,
            'user_id': user_id,
            'enable_system_message': enable_system_message,
            'folder_id': folder_id
        }
        
        # Membuat objek percakapan
        conversation = Conversation(**conversation_data)
        
        # Menambahkan ke database
        db_session = base_db.session
        db_session.add(conversation)
        db_session.commit()
        
        print(f"Berhasil membuat percakapan dengan ID: {conversation.id}")
        return conversation
    except Exception as e:
        db_session.rollback()
        print(f"Gagal membuat percakapan: {str(e)}")
        return None

def get_conversation_by_id(conversation_id):
    """Mengambil percakapan berdasarkan ID dari database"""
    try:
        # Inisialisasi database jika belum diinisialisasi
        init_db()
        
        # Mengambil percakapan dari database menggunakan Session.get()
        db_session = base_db.session
        conversation = db_session.get(Conversation, conversation_id)
        
        if conversation:
            print(f"Berhasil mengambil percakapan dengan ID: {conversation.id}")
            print(f"Title: {conversation.title}")
            print(f"System Message: {conversation.system_message}")
            print(f"User ID: {conversation.user_id}")
            print(f"Enable System Message: {conversation.enable_system_message}")
            print(f"Folder ID: {conversation.folder_id}")
            print(f"Created At: {conversation.created_at}")
            print(f"Updated At: {conversation.updated_at}")
            return conversation
        else:
            print(f"Tidak ditemukan percakapan dengan ID: {conversation_id}")
            return None
    except Exception as e:
        print(f"Gagal mengambil percakapan: {str(e)}")
        return None

def get_all_conversations():
    """Mengambil semua percakapan dari database"""
    try:
        # Inisialisasi database jika belum diinisialisasi
        init_db()
        
        # Mengambil semua percakapan dari database
        db_session = base_db.session
        conversations = db_session.query(Conversation).all()
        
        if conversations:
            print(f"Berhasil mengambil {len(conversations)} percakapan:")
            for conversation in conversations:
                print(f"  - ID: {conversation.id}, Title: {conversation.title}")
            return conversations
        else:
            print("Tidak ada percakapan dalam database")
            return []
    except Exception as e:
        print(f"Gagal mengambil percakapan: {str(e)}")
        return []

def main():
    """Fungsi utama untuk demonstrasi"""
    print("=== Script untuk membuat dan mengambil percakapan ===")
    
    # Membuat percakapan baru
    print("\n1. Membuat percakapan baru...")
    conversation = create_conversation(
        title="Percakapan Tes",
        system_message="Anda adalah asisten yang membantu",
        user_id=1,
        enable_system_message=1
    )
    
    if conversation:
        # Mengambil percakapan yang baru dibuat
        print("\n2. Mengambil percakapan yang baru dibuat...")
        retrieved_conversation = get_conversation_by_id(conversation.id)
        
        # Mengambil semua percakapan
        print("\n3. Mengambil semua percakapan...")
        all_conversations = get_all_conversations()
    else:
        print("Gagal membuat percakapan, melewati pengambilan")

if __name__ == "__main__":
    main()