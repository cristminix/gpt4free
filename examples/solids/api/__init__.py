"""
Main API module that orchestrates all the components
"""
from .core import Api
from .base import ErrorResponse, format_exception
from .models import (
    read_root, read_root_v1, models_list, provider_models, 
    model_info, providers_list, providers_info
)
from .chat import chat_completions, v1_responses
from .media import (
    generate_image, convert, markitdown, generate_speech,
    upload_cookies, get_json, get_media, get_media_thumbnail
)

# Re-export the main components
__all__ = [
    "Api",
    "ErrorResponse",
    "format_exception",
    "read_root",
    "read_root_v1", 
    "models_list",
    "provider_models",
    "model_info",
    "providers_list",
    "providers_info",
    "chat_completions",
    "v1_responses",
    "generate_image",
    "convert",
    "markitdown",
    "generate_speech",
    "upload_cookies",
    "get_json",
    "get_media",
    "get_media_thumbnail"
]