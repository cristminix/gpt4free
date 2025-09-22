from flask import Blueprint, request, jsonify
from examples.custom_inference_api.db.models import MessageGroup, Message, message_group_messages
from examples.custom_inference_api.db.db_connection import base_db, engine
from sqlalchemy.orm import sessionmaker

message_group_messages_bp = Blueprint('message_group_messages', __name__)

# Create a new message group message relationship
@message_group_messages_bp.route('/', methods=['POST'])
def create_message_group_message():
    db_session = None
    try:
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'messageId' not in data or 'groupId' not in data:
            return jsonify({
                'success': False,
                'error': 'Message ID and Message Group ID are required'
            }), 400
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Periksa apakah message dan message group ada
        message = db_session.query(Message).get(data['messageId'])
        message_group = db_session.query(MessageGroup).get(data['groupId'])
        
        if not message:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message not found'
            }), 404
        
        if not message_group:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message group not found'
            }), 404
        
        # Buat relasi
        stmt = message_group_messages.insert().values(
            message_id=data['messageId'],
            message_group_id=data['groupId']
        )
        db_session.execute(stmt)
        db_session.commit()
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'messageId': data['messageId'],
                'groupId': data['groupId']
            }
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to create message group message relationship'
        }), 500

# Get all message group messages
@message_group_messages_bp.route('/', methods=['GET'])
def get_message_group_messages():
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Query langsung ke tabel asosiasi
        result = db_session.execute(message_group_messages.select()).fetchall()
        
        # Mengakses atribut sebelum menutup session
        mgm_data = [{
            'messageId': row.message_id,
            'groupId': row.message_group_id
        } for row in result]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': mgm_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message group messages'
        }), 500

# Get message group messages by message group ID
@message_group_messages_bp.route('/message-groups/<string:message_group_id>', methods=['GET'])
def get_message_group_messages_by_group_id(message_group_id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Periksa apakah message group ada
        message_group = db_session.query(MessageGroup).get(message_group_id)
        if not message_group:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message group not found'
            }), 404
        
        # Query ke tabel asosiasi berdasarkan message_group_id
        result = db_session.execute(
            message_group_messages.select().where(
                message_group_messages.c.message_group_id == message_group_id
            )
        ).fetchall()
        
        # Mengakses atribut sebelum menutup session
        mgm_data = [{
            'messageId': row.message_id,
            'groupId': row.message_group_id
        } for row in result]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': mgm_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message group messages'
        }), 500

# Get message group messages by message ID
@message_group_messages_bp.route('/messages/<string:message_id>', methods=['GET'])
def get_message_group_messages_by_message_id(message_id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Periksa apakah message ada
        message = db_session.query(Message).get(message_id)
        if not message:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message not found'
            }), 404
        
        # Query ke tabel asosiasi berdasarkan message_id
        result = db_session.execute(
            message_group_messages.select().where(
                message_group_messages.c.message_id == message_id
            )
        ).fetchall()
        
        # Mengakses atribut sebelum menutup session
        mgm_data = [{
            'messageId': row.message_id,
            'groupId': row.message_group_id
        } for row in result]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': mgm_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message group messages'
        }), 500

# Delete message group message relationship
@message_group_messages_bp.route('/', methods=['DELETE'])
def delete_message_group_message():
    db_session = None
    try:
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'messageId' not in data or 'groupId' not in data:
            return jsonify({
                'success': False,
                'error': 'Message ID and Message Group ID are required'
            }), 400
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Hapus relasi
        stmt = message_group_messages.delete().where(
            message_group_messages.c.message_id == data['messageId'],
            message_group_messages.c.message_group_id == data['groupId']
        )
        result = db_session.execute(stmt)
        db_session.commit()
        
        # Menutup session
        db_session.close()
        
        if result.rowcount == 0:
            return jsonify({
                'success': False,
                'error': 'Message group message relationship not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Message group message relationship deleted successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to delete message group message relationship'
        }), 500