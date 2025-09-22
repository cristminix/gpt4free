#!/usr/bin/env python3
"""
Script untuk menguji fungsi create_conversation secara langsung
"""

import sys
import os
import json
from unittest.mock import Mock

# Tambahkan direktori proyek ke path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from examples.solids.extended.llm_routes.conversations import create_conversation

def test_create_conversation():
    """Menguji fungsi create_conversation secara langsung"""
    print("=== Menguji fungsi create_conversation ===")
    
    # Membuat mock request object
    mock_request = Mock()
    mock_request.get_json.return_value = {
        'title': 'Percakapan Tes dari Unit Test',
        'system_message': 'Anda adalah asisten yang membantu',
        'user_id': 1,
        'enable_system_message': 1
    }
    
    # Menyimpan referensi request asli
    import examples.solids.extended.llm_routes.conversations as conv_module
    original_request = conv_module.request
    
    try:
        # Mengganti request dengan mock
        conv_module.request = mock_request
        
        # Memanggil fungsi create_conversation
        result = create_conversation()
        
        print(f"Hasil dari create_conversation: {result}")
        print(f"Tipe hasil: {type(result)}")
        
        # Jika hasil adalah tuple (response, status_code), ekstrak response
        if isinstance(result, tuple):
            response, status_code = result
            print(f"Status code: {status_code}")
            print(f"Response: {response}")
            
            # Jika response adalah objek dengan metode get_json()
            if hasattr(response, 'get_json'):
                json_data = response.get_json()
                print(f"JSON data: {json_data}")
            elif isinstance(response, dict):
                print(f"Response data: {response}")
        else:
            print(f"Response langsung: {result}")
            
    except Exception as e:
        print(f"Error saat menguji create_conversation: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Mengembalikan request asli
        conv_module.request = original_request

if __name__ == "__main__":
    test_create_conversation()