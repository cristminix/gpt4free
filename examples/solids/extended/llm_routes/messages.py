from flask import Blueprint, request, jsonify
from examples.custom_inference_api.db.models import MessageGroup, Message, Participant, message_group_messages
from examples.custom_inference_api.db.db_connection import base_db, engine
from sqlalchemy.orm import sessionmaker
import uuid
import time


messages_bp = Blueprint('messages', __name__)

# Add a message to a conversation
@messages_bp.route('/conversations/<string:conversation_id>', methods=['POST'])
def create_message(conversation_id):
    db_session = None
    try:
        data = request.get_json()
        
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Create or get participant (LLM or user)
        participant = None
        if 'username' in data:
            # Check if participant with this username already exists
            participant = db_session.query(Participant).filter_by(username=data['username']).first()
            
            # If not, create a new participant
            if not participant:
                participant_data = {
                    'username': data['username'],
                    'role': data.get('role', 'user')
                }
                participant = Participant(**participant_data)
                db_session.add(participant)
                db_session.flush()  # Get the ID without committing
        else:
            # Create a new participant for this message
            participant_data = {
                'username': data.get('username', f'participant_{int(time.time() * 1000)}'),
                'role': data.get('role', 'user')
            }
            participant = Participant(**participant_data)
            db_session.add(participant)
            db_session.flush()  # Get the ID without committing
        
        # Create the message
        message_data = {
            'id': data.get('id', str(uuid.uuid4())),
            'content': data['content'],
            'conversation_id': conversation_id,
            'participant_id': participant.id,
            'parent_id': data.get('parentId')
        }
        
        # Check if message already exists
        message = db_session.query(Message).get(message_data['id'])
        if not message:
            message = Message(**message_data)
            db_session.add(message)
        
        groupId = data['groupId']
        if groupId and message:
            group_exists = db_session.query(MessageGroup).get(groupId) is not None
            print({"group_exists": group_exists})
            if group_exists:
                # Create the relationship
                stmt = message_group_messages.insert().values(
                    message_id=message.id,
                    message_group_id=groupId
                )
                db_session.execute(stmt)
                db_session.commit()
                print({"message_group_message": {"message_id": message.id, "message_group_id": groupId}})
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': message.id,
            'content': message.content,
            'conversationId': message.conversation_id,
            'participantId': message.participant_id,
            'parentId': message.parent_id,
            'createdAt': message.created_at
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': [response_data]
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': f'Failed to create message {e}'
        }), 400

# Get all messages in a conversation with participant info
@messages_bp.route('/conversations/<string:conversation_id>', methods=['GET'])
def get_messages_by_conversation_id(conversation_id):
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get all messages with participant info
        messages = db_session.query(
            Message.id,
            Message.content,
            Participant.username,
            Participant.role,
            Message.created_at,
            Message.parent_id,
            Message.collapsed,
            message_group_messages.c.message_group_id,
        ).join(Participant, Message.participant_id == Participant.id)\
         .join(message_group_messages, Message.id == message_group_messages.c.message_id)\
         .filter(Message.conversation_id == conversation_id)\
         .order_by(Message.created_at.asc()).all()
        
        # Mengakses atribut sebelum menutup session
        messages_data = [{
            'id': msg.id,
            'content': msg.content,
            'username': msg.username,
            'role': msg.role,
            'createdAt': msg.created_at,
            'parentId': msg.parent_id,
            'collapsed': msg.collapsed,
            'groupId': msg.message_group_id
        } for msg in messages]
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': messages_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch messages {e}'

        }), 500

# Delete a message by ID
@messages_bp.route('/conversations/<string:conversation_id>/<string:message_id>', methods=['DELETE'])
def delete_message(conversation_id, message_id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message = db_session.query(Message).get(message_id)
        if not message:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message not found'
            }), 404
        
        db_session.delete(message)
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully'
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to delete message'
        }), 500

# Update a message by ID
@messages_bp.route('/conversations/<string:conversation_id>/<string:message_id>', methods=['PUT'])
def update_message(conversation_id, message_id):
    db_session = None
    try:
        # Membuat session baru untuk operasi database
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        message = db_session.query(Message).get(message_id)
        if not message:
            db_session.close()
            return jsonify({
                'success': False,
                'error': 'Message not found'
            }), 404
        
        data = request.get_json()
        if 'content' in data:
            message.content = data['content']
        if 'collapsed' in data:
            message.collapsed = data['collapsed']
        if 'hasError' in data:
            message.has_error = data['hasError']
        
        db_session.commit()
        
        # Mengakses atribut sebelum menutup session
        response_data = {
            'id': message.id,
            'content': message.content,
            'conversationId': message.conversation_id,
            'participantId': message.participant_id,
            'parentId': message.parent_id,
            'createdAt': message.created_at,
            'collapsed': message.collapsed,
            'hasError': message.has_error
        }
        
        # Menutup session
        db_session.close()
        
        return jsonify({
            'success': True,
            'data': [response_data]
        })
    except Exception as e:
        if db_session:
            db_session.rollback()
            db_session.close()
        return jsonify({
            'success': False,
            'error': 'Failed to update message'
        }), 500