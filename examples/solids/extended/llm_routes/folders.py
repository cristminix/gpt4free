from flask import Blueprint, request, jsonify
from examples.custom_inference_api.db.models import Folder
from examples.custom_inference_api.db.db_connection import base_db, engine
from sqlalchemy.orm import sessionmaker
import uuid

folders_bp = Blueprint('folders', __name__)

# Create a new folder
@folders_bp.route('/', methods=['POST'])
def create_folder():
    db_session = None
    try:
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        folder_data = {
            'id': data.get('id', str(uuid.uuid4())),
            'name': data['name'],
            'description': data.get('description', '')
        }
        
        folder = Folder(**folder_data)
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Menambahkan folder ke database
        db_session.add(folder)
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to create folder'
        }), 500

# Get all folders
@folders_bp.route('/', methods=['GET'])
def get_folders():
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        folders = db_session.query(Folder).all()
        
        # Mengakses atribut sebelum menutup session
        folders_data = [{
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at
        } for folder in folders]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': folders_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch folders'
        }), 500

# Get folder by ID
@folders_bp.route('/<string:id>', methods=['GET'])
def get_folder_by_id(id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        folder = db_session.query(Folder).get(id)
        
        if not folder:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Folder not found'
            }), 404
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch folder'
        }), 500

# Update folder by ID
@folders_bp.route('/<string:id>', methods=['PUT'])
def update_folder(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        folder = db_session.query(Folder).get(id)
        if not folder:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Folder not found'
            }), 404
        
        data = request.get_json()
        if 'name' in data:
            folder.name = data['name']
        if 'description' in data:
            folder.description = data['description']
        
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Folder updated successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to update folder'
        }), 500

# Delete folder by ID
@folders_bp.route('/<string:id>', methods=['DELETE'])
def delete_folder(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        folder = db_session.query(Folder).get(id)
        if not folder:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Folder not found'
            }), 404
        
        db_session.delete(folder)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'message': 'Folder deleted successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to delete folder'
        }), 500