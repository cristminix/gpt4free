"""
Custom Inference API - Reorganized version
"""
from __future__ import annotations

# Import all necessary modules from the solids package
from examples.solids import (
    AppConfig,
    get_name_and_provider,
    get_model_by_providers,
    create_app,
    create_app_debug,
    create_app_with_gui_and_debug,
    create_app_with_demo_and_debug,
    run_api,
    ErrorResponse,
    Api,
    format_exception,
)

# Define what should be available when importing *
__all__ = [
    "AppConfig",
    "get_name_and_provider",
    "get_model_by_providers",
    "create_app",
    "create_app_debug",
    "create_app_with_gui_and_debug",
    "create_app_with_demo_and_debug",
    "run_api",
    "ErrorResponse",
    "Api",
    "format_exception",
]