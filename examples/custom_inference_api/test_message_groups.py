#!/usr/bin/env python3
"""
Script untuk menguji endpoint message groups dengan context Flask yang sesuai
"""

import sys
import os
import json
import uuid

# Tambahkan direktori proyek ke path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask
from examples.solids.extended.llm_routes.conversations import conversations_bp
from examples.solids.extended.llm_routes.message_groups import message_groups_bp
from examples.solids.extended.llm_routes.llm_chat import llm_chat_bp

def create_conversation():
    """Membuat percakapan terlebih dahulu"""
    print("=== Membuat percakapan terlebih dahulu ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(llm_chat_bp)
    
    # Membuat test client
    with app.test_client() as client:
        # Membuat data untuk percakapan
        data = {
            'title': 'Percakapan untuk Message Group Test',
            'system_message': 'Anda adalah asisten yang membantu',
            'user_id': 1,
            'enable_system_message': 1
        }
        
        # Mengirim POST request ke endpoint conversations
        response = client.post('/api/llm/conversations/', 
                             json=data,
                             content_type='application/json')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah percakapan berhasil dibuat
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                conversation_id = json_data['data']['id']
                print(f"Berhasil membuat percakapan dengan ID: {conversation_id}")
                return conversation_id
            else:
                print(f"Gagal membuat percakapan: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")
        
        return None

def test_create_message_group_with_context(conversation_id):
    """Menguji endpoint untuk membuat message group baru"""
    if not conversation_id:
        print("Tidak ada ID percakapan untuk digunakan")
        return None
    
    print(f"\n=== Menguji endpoint untuk membuat message group dengan Conversation ID: {conversation_id} ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(llm_chat_bp)
    
    # Membuat test client
    with app.test_client() as client:
        # Membuat data untuk dikirim (menggunakan conversationId bukan conversation_id)
        data = {
            'conversationId': conversation_id,
        }
        
        # Mengirim POST request ke endpoint message groups
        response = client.post('/api/llm/message-groups/', 
                             json=data,
                             content_type='application/json')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah message group berhasil dibuat
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                message_group_id = json_data['data']['id']
                conversation_id = json_data['data']['conversationId']
                print(f"Berhasil membuat message group dengan ID: {message_group_id}")
                print(f"Conversation ID: {conversation_id}")
                return message_group_id
            else:
                print(f"Gagal membuat message group: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")
        
        return None

def test_get_message_groups_with_context():
    """Menguji endpoint untuk mengambil semua message group"""
    print("\n=== Menguji endpoint untuk mengambil semua message group ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(llm_chat_bp)
    
    # Membuat test client
    with app.test_client() as client:
        # Mengirim GET request ke endpoint message groups
        response = client.get('/api/llm/message-groups/')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah message groups berhasil diambil
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                message_groups = json_data['data']
                print(f"Berhasil mengambil {len(message_groups)} message group(s)")
                for mg in message_groups:
                    print(f"  - ID: {mg['id']}, Conversation ID: {mg['conversationId']}")
                return message_groups
            else:
                print(f"Gagal mengambil message groups: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")
        
        return []

def test_get_message_group_by_id_with_context(message_group_id):
    """Menguji endpoint untuk mengambil message group berdasarkan ID"""
    if not message_group_id:
        print("Tidak ada ID message group untuk diuji")
        return
    
    print(f"\n=== Menguji endpoint untuk mengambil message group dengan ID: {message_group_id} ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(llm_chat_bp)
    
    # Membuat test client
    with app.test_client() as client:
        # Mengirim GET request ke endpoint message group by ID
        response = client.get(f'/api/llm/message-groups/{message_group_id}')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah message group berhasil diambil
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                mg_data = json_data['data']
                print(f"Berhasil mengambil message group: ID={mg_data['id']}, Conversation ID={mg_data['conversationId']}")
                return mg_data
            else:
                print(f"Gagal mengambil message group: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")
        
        return None

def test_get_message_groups_by_conversation_id_with_context(conversation_id):
    """Menguji endpoint untuk mengambil message groups berdasarkan conversation ID"""
    if not conversation_id:
        print("Tidak ada ID conversation untuk diuji")
        return
    
    print(f"\n=== Menguji endpoint untuk mengambil message groups dengan Conversation ID: {conversation_id} ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(llm_chat_bp)
    
    # Membuat test client
    with app.test_client() as client:
        # Mengirim GET request ke endpoint message groups by conversation ID
        response = client.get(f'/api/llm/message-groups/conversation/{conversation_id}')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah message groups berhasil diambil
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                message_groups = json_data['data']
                print(f"Berhasil mengambil {len(message_groups)} message group(s) untuk conversation {conversation_id}")
                for mg in message_groups:
                    print(f"  - ID: {mg['id']}, Conversation ID: {mg['conversationId']}")
                return message_groups
            else:
                print(f"Gagal mengambil message groups: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")
        
        return []

if __name__ == "__main__":
    # Membuat percakapan terlebih dahulu
    conversation_id = create_conversation()
    
    # Menguji pembuatan message group dengan conversation ID yang valid
    message_group_id = test_create_message_group_with_context(conversation_id)
    
    # Menguji pengambilan semua message group
    all_message_groups = test_get_message_groups_with_context()
    
    # Menguji pengambilan message group berdasarkan ID
    if message_group_id:
        test_get_message_group_by_id_with_context(message_group_id)
    
    # Menguji pengambilan message groups berdasarkan conversation ID
    if conversation_id:
        test_get_message_groups_by_conversation_id_with_context(conversation_id)