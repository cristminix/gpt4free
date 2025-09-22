from flask import Blueprint, request, jsonify
from examples.custom_inference_api.db.models import Attachment
from examples.custom_inference_api.db.db_connection import base_db, engine
from sqlalchemy.orm import sessionmaker
import uuid

attachments_bp = Blueprint('attachments', __name__)

# Create a new attachment
@attachments_bp.route('/', methods=['POST'])
def create_attachment():
    db_session = None
    try:
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'filename' not in data or 'mimetype' not in data:
            return jsonify({
                'success': False,
                'error': 'Filename and mimetype are required'
            }), 400
        
        attachment_data = {
            'id': data.get('id', str(uuid.uuid4())),
            'filename': data['filename'],
            'mimetype': data['mimetype']
        }
        
        attachment = Attachment(**attachment_data)
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Menambahkan attachment ke database
        db_session.add(attachment)
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': attachment.id,
            'filename': attachment.filename,
            'mimetype': attachment.mimetype,
            'created_at': attachment.created_at,
            'updated_at': attachment.updated_at
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
            'error': 'Failed to create attachment'
        }), 500

# Get all attachments
@attachments_bp.route('/', methods=['GET'])
def get_attachments():
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        attachments = db_session.query(Attachment).all()
        
        # Mengakses atribut sebelum menutup session
        attachments_data = [{
            'id': att.id,
            'filename': att.filename,
            'mimetype': att.mimetype,
            'created_at': att.created_at,
            'updated_at': att.updated_at
        } for att in attachments]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': attachments_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch attachments'
        }), 500

# Get attachment by ID
@attachments_bp.route('/<string:id>', methods=['GET'])
def get_attachment_by_id(id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        attachment = db_session.query(Attachment).get(id)
        
        if not attachment:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Attachment not found'
            }), 404
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': attachment.id,
            'filename': attachment.filename,
            'mimetype': attachment.mimetype,
            'created_at': attachment.created_at,
            'updated_at': attachment.updated_at
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
            'error': 'Failed to fetch attachment'
        }), 500

# Update attachment by ID
@attachments_bp.route('/<string:id>', methods=['PUT'])
def update_attachment(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        attachment = db_session.query(Attachment).get(id)
        if not attachment:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Attachment not found'
            }), 404
        
        data = request.get_json()
        if 'filename' in data:
            attachment.filename = data['filename']
        if 'mimetype' in data:
            attachment.mimetype = data['mimetype']
        
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': attachment.id,
            'filename': attachment.filename,
            'mimetype': attachment.mimetype,
            'created_at': attachment.created_at,
            'updated_at': attachment.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Attachment updated successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to update attachment'
        }), 500

# Delete attachment by ID
@attachments_bp.route('/<string:id>', methods=['DELETE'])
def delete_attachment(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        attachment = db_session.query(Attachment).get(id)
        if not attachment:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Attachment not found'
            }), 404
        
        db_session.delete(attachment)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'message': 'Attachment deleted successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to delete attachment'
        }), 500