"""
Solids package for custom inference API
"""

# Import and export key components
from .config import AppConfig
from .utils import get_name_and_provider, get_model_by_providers, has_crypto, has_pillow
from .app import (
    create_app, create_app_debug, 
    create_app_with_gui_and_debug, 
    create_app_with_demo_and_debug
)
from .run import run_api
from .api.core import Api
from .api.base import ErrorResponse, format_exception

# Define what should be available when importing *
__all__ = [
    "AppConfig",
    "get_name_and_provider",
    "get_model_by_providers",
    "has_crypto",
    "has_pillow",
    "create_app",
    "create_app_debug",
    "create_app_with_gui_and_debug",
    "create_app_with_demo_and_debug",
    "run_api",
    "ErrorResponse",
    "Api",
    "format_exception",
]