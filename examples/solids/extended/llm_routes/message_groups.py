from flask import Blueprint, request, jsonify, current_app
from examples.custom_inference_api.db.models import MessageGroup
from examples.custom_inference_api.db.db_connection import base_db, engine
from sqlalchemy.orm import sessionmaker
import uuid

message_groups_bp = Blueprint('message_groups', __name__)

# Create a new message group
@message_groups_bp.route('/', methods=['POST'])
def create_message_group():
    db_session = None
    try:
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'conversationId' not in data:
            return jsonify({
                'success': False,
                'error': 'Conversation ID is required'
            }), 400
        
        message_group_data = {
            'id': data.get('id', str(uuid.uuid4())),
            'conversation_id': data['conversationId']
        }
        
        message_group = MessageGroup(**message_group_data)
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Menambahkan message group ke database
        db_session.add(message_group)
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': message_group.id,
            'conversationId': message_group.conversation_id,
            'createdAt': message_group.created_at,
            'updatedAt': message_group.updated_at
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
            'error': 'Failed to create message group'
        }), 500

# Get all message groups
@message_groups_bp.route('/', methods=['GET'])
def get_message_groups():
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message_groups = db_session.query(MessageGroup).all()
        
        # Mengakses atribut sebelum menutup session
        message_groups_data = [{
            'id': mg.id,
            'conversationId': mg.conversation_id,
            'createdAt': mg.created_at,
            'updatedAt': mg.updated_at
        } for mg in message_groups]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': message_groups_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message groups'
        }), 500

# Get message groups by conversation ID
@message_groups_bp.route('/conversation/<string:conversation_id>', methods=['GET'])
def get_message_groups_by_conversation_id(conversation_id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message_groups = db_session.query(MessageGroup).filter_by(conversation_id=conversation_id).all()
        
        # Mengakses atribut sebelum menutup session
        message_groups_data = [{
            'id': mg.id,
            'conversationId': mg.conversation_id,
            'createdAt': mg.created_at,
            'updatedAt': mg.updated_at
        } for mg in message_groups]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': message_groups_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message groups'
        }), 500

# Get message group by ID
@message_groups_bp.route('/<string:id>', methods=['GET'])
def get_message_group_by_id(id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message_group = db_session.query(MessageGroup).get(id)
        
        if not message_group:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message group not found'
            }), 404
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': message_group.id,
            'conversationId': message_group.conversation_id,
            'createdAt': message_group.created_at,
            'updatedAt': message_group.updated_at
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
            'error': 'Failed to fetch message group'
        }), 500

# Update message group by ID
@message_groups_bp.route('/<string:id>', methods=['PUT'])
def update_message_group(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message_group = db_session.query(MessageGroup).get(id)
        if not message_group:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message group not found'
            }), 404
        
        data = request.get_json()
        if 'conversation_id' in data:
            message_group.conversation_id = data['conversation_id']
        
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': message_group.id,
            'conversationId': message_group.conversation_id,
            'createdAt': message_group.created_at,
            'updatedAt': message_group.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Message group updated successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to update message group'
        }), 500

# Delete message group by ID
@message_groups_bp.route('/<string:id>', methods=['DELETE'])
def delete_message_group(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message_group = db_session.query(MessageGroup).get(id)
        if not message_group:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message group not found'
            }), 404
        
        db_session.delete(message_group)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'message': 'Message group deleted successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to delete message group'
        }), 500