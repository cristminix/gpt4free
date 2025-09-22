from flask import Blueprint, request, jsonify, current_app
from examples.custom_inference_api.db.models import Conversation, Message, MessageGroup, message_group_messages
from examples.custom_inference_api.db.db_connection import base_db, engine, get_db, init_db
from sqlalchemy.orm import sessionmaker
import uuid

conversations_bp = Blueprint('conversations', __name__)

# Create a new conversation
@conversations_bp.route('/', methods=['POST'])
def create_conversation():
    db_session = None
    try:
        init_db()
        data = request.get_json()
        
        # Validasi data yang diperlukan
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        conversation_data = {
            'id': data.get('id', str(uuid.uuid4())),
            'title': data['title'],
            'system_message': data.get('system_message', data.get('systemMessage', '')),
            'user_id': data.get('user_id', data.get('userId', 1)),
            'enable_system_message': data.get('enable_system_message', data.get('enableSystemMessage', 1)),
            'folder_id': data.get('folder_id', data.get('folderId'))
        }
        
        conversation = Conversation(**conversation_data)
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Menambahkan percakapan ke database
        db_session.add(conversation)
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': conversation.id,
            'title': conversation.title,
            'createdAt': conversation.created_at,
            'updatedAt': conversation.updated_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except KeyError as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': f'Missing required field: {str(e)}'
        }), 400
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to create conversation',
            'details': str(e)
        }), 500

# Get all conversations
@conversations_bp.route('/users/<int:user_id>', methods=['GET'])
def get_conversations_by_user_id(user_id):
    try:
        # Gunakan engine dari db_connection.py
        Session = sessionmaker(bind=engine)
        session = Session()
        
        conversations = session.query(Conversation).filter_by(user_id=user_id)\
                                          .order_by(Conversation.updated_at.desc()).all()
        
        # Mengakses atribut sebelum menutup session
        conversations_data = [{
            'id': conv.id,
            'title': conv.title,
            'createdAt': conv.created_at,
            'updatedAt': conv.updated_at
        } for conv in conversations]
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': conversations_data
        })
    except Exception as e:
        print(f"Error fetching conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversations'
        }), 500

# Get conversation by ID
@conversations_bp.route('/<string:id>', methods=['GET'])
def get_conversation_by_id(id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        conversation = db_session.query(Conversation).get(id)
        
        if not conversation:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': conversation.id,
            'title': conversation.title,
            'systemMessage': conversation.system_message,
            'userId': conversation.user_id,
            'enableSystemMessage': conversation.enable_system_message,
            'folderId': conversation.folder_id,
            'createdAt': conversation.created_at,
            'updatedAt': conversation.updated_at
        }
        
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversation'
        }), 500

# Get message groups by conversation ID
@conversations_bp.route('/<string:id>/message-groups', methods=['GET'])
def get_message_groups_by_conversation_id(id):
    try:
        # Gunakan engine dari db_connection.py
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Periksa apakah conversation ada
        conversation = session.query(Conversation).get(id)
        if not conversation:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        message_groups = session.query(MessageGroup).filter_by(conversation_id=id).all()
        
        # Mengakses atribut sebelum menutup session
        message_groups_data = [{
            'id': mg.id,
            'conversationId': mg.conversation_id,
            'createdAt': mg.created_at,
            'updatedAt': mg.updated_at
        } for mg in message_groups]
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': message_groups_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch message groups'
        }), 500

# Get count of conversations by user ID
@conversations_bp.route('/users/<int:user_id>/counts', methods=['GET'])
def get_conversation_count_by_user_id(user_id):
    try:
        # Gunakan engine dari db_connection.py
        Session = sessionmaker(bind=engine)
        session = Session()
        
        count = session.query(Conversation).filter_by(user_id=user_id).count()
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'count': count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversation count'
        }), 500

# Update conversation by ID
@conversations_bp.route('/<string:id>', methods=['PUT'])
def update_conversation(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        conversation = db_session.query(Conversation).get(id)
        if not conversation:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        data = request.get_json()
        if 'title' in data:
            conversation.title = data['title']
        if 'system_message' in data:
            conversation.system_message = data['system_message']
        elif 'systemMessage' in data:
            conversation.system_message = data['systemMessage']
        if 'enable_system_message' in data:
            conversation.enable_system_message = data['enable_system_message']
        elif 'enableSystemMessage' in data:
            conversation.enable_system_message = data['enableSystemMessage']
        if 'folder_id' in data:
            conversation.folder_id = data['folder_id']
        elif 'folderId' in data:
            conversation.folder_id = data['folderId']
        
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': conversation.id,
            'title': conversation.title,
            'createdAt': conversation.created_at,
            'updatedAt': conversation.updated_at
        }
        
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Conversation updated successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to update conversation'
        }), 500

# Delete conversation by ID
@conversations_bp.route('/<string:id>', methods=['DELETE'])
def delete_conversation(id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Check if conversation exists
        conversation = db_session.query(Conversation).get(id)
        if not conversation:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Get message groups by conversation
        message_groups = db_session.query(MessageGroup).filter_by(conversation_id=id).all()
        for group in message_groups:
            group_id = group.id
            # Get message group messages
            mgm_records = db_session.query(message_group_messages).filter_by(
                message_group_id=group_id
            ).all()
            
            for mgm in mgm_records:
                message_id = mgm.message_id
                # Delete message group message relationship
                stmt = message_group_messages.delete().where(
                    message_group_messages.c.message_id == message_id,
                    message_group_messages.c.message_group_id == group_id
                )
                db_session.execute(stmt)
                
                # Delete message with error handling
                try:
                    message = db_session.query(Message).get(message_id)
                    if message:
                        db_session.delete(message)
                except Exception as e:
                    print(f"Error deleting message {message_id}: {str(e)}")
            
            # Delete the message group
            db_session.delete(group)
        
        # Delete remaining messages by conversation ID
        db_session.query(Message).filter_by(conversation_id=id).delete()
        
        # Delete the conversation
        db_session.delete(conversation)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully',
            'data': {
                'id': conversation.id,
                'title': conversation.title,
                'createdAt': conversation.created_at,
                'updatedAt': conversation.updated_at
            }
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': f'Failed to delete conversation {e}'
        }), 500