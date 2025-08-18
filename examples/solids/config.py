"""
Configuration module for the API
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_PORT = 1337
DEFAULT_TIMEOUT = 600

class AppConfig:
    ignored_providers: Optional[list[str]] = None
    g4f_api_key: Optional[str] = None
    ignore_cookie_files: bool = False
    model: str = None
    provider: str = None
    media_provider: str = None
    proxy: str = None
    gui: bool = False
    demo: bool = False
    timeout: int = DEFAULT_TIMEOUT

    @classmethod
    def set_config(cls, **data):
        for key, value in data.items():
            if value is not None:
                setattr(cls, key, value)