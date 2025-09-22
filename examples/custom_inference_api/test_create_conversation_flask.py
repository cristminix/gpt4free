#!/usr/bin/env python3
"""
Script untuk menguji fungsi create_conversation dengan context Flask yang sesuai
"""

import sys
import os
import json

# Tambahkan direktori proyek ke path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask, request, jsonify
from examples.solids.extended.llm_routes.conversations import create_conversation, conversations_bp

def test_create_conversation_with_context():
    """Menguji fungsi create_conversation dengan context Flask yang sesuai"""
    print("=== Menguji fungsi create_conversation dengan context Flask ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(conversations_bp, url_prefix='/conversations')
    
    # Membuat test client
    with app.test_client() as client:
        # Membuat data untuk dikirim
        data = {
            'title': 'Percakapan Tes dari Flask Test Client',
            'system_message': 'Anda adalah asisten yang membantu',
            'user_id': 1,
            'enable_system_message': 1
        }
        
        # Mengirim POST request ke endpoint create_conversation
        response = client.post('/conversations/', 
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

def test_get_conversation_with_context(conversation_id):
    """Menguji fungsi get_conversation_by_id dengan context Flask yang sesuai"""
    if not conversation_id:
        print("Tidak ada ID percakapan untuk diuji")
        return
    
    print(f"\n=== Menguji fungsi get_conversation_by_id dengan ID: {conversation_id} ===")
    
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Mendaftarkan blueprint
    app.register_blueprint(conversations_bp, url_prefix='/conversations')
    
    # Membuat test client
    with app.test_client() as client:
        # Mengirim GET request ke endpoint get_conversation_by_id
        response = client.get(f'/conversations/{conversation_id}')
        
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Memeriksa apakah percakapan berhasil diambil
        if response.status_code == 200:
            json_data = response.get_json()
            if json_data and json_data.get('success'):
                print(f"Berhasil mengambil percakapan: {json_data['data']['title']}")
            else:
                print(f"Gagal mengambil percakapan: {json_data}")
        else:
            print(f"Error HTTP {response.status_code}: {response.get_json()}")

if __name__ == "__main__":
    # Menguji pembuatan percakapan
    conversation_id = test_create_conversation_with_context()
    
    # Menguji pengambilan percakapan
    test_get_conversation_with_context(conversation_id)