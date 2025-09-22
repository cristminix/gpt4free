from flask import Blueprint
from .folders import folders_bp
from .conversations import conversations_bp
from .messages import messages_bp
from .message_groups import message_groups_bp
from .message_group_messages import message_group_messages_bp
from .attachments import attachments_bp

llm_chat_bp = Blueprint('llm_chat', __name__, url_prefix='/api/llm')

# Register all the routes with the llm_chat blueprint
llm_chat_bp.register_blueprint(folders_bp, url_prefix='/folders')
llm_chat_bp.register_blueprint(conversations_bp, url_prefix='/conversations')
llm_chat_bp.register_blueprint(messages_bp, url_prefix='/messages')
llm_chat_bp.register_blueprint(message_groups_bp, url_prefix='/message-groups')
llm_chat_bp.register_blueprint(message_group_messages_bp, url_prefix='/message-group-messages')
llm_chat_bp.register_blueprint(attachments_bp, url_prefix='/attachments')