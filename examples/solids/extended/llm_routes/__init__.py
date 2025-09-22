from flask import Blueprint
from .conversations import conversations_bp
from .messages import messages_bp
from .attachments import attachments_bp
from .folders import folders_bp
from .message_groups import message_groups_bp
from .message_group_messages import message_group_messages_bp
from .llm_chat import llm_chat_bp

# Create main blueprint
llm_routes_bp = Blueprint('llm_routes', __name__)

# Register all blueprints
llm_routes_bp.register_blueprint(conversations_bp, url_prefix='/conversations')
llm_routes_bp.register_blueprint(messages_bp, url_prefix='/messages')
llm_routes_bp.register_blueprint(attachments_bp, url_prefix='/attachments')
llm_routes_bp.register_blueprint(folders_bp, url_prefix='/folders')
llm_routes_bp.register_blueprint(message_groups_bp, url_prefix='/message-groups')
llm_routes_bp.register_blueprint(message_group_messages_bp, url_prefix='/message-group-messages')
llm_routes_bp.register_blueprint(llm_chat_bp, url_prefix='/llm-chat')