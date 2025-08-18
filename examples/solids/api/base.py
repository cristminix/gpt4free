"""
Base API components
"""
import logging
import json
from typing import Union, Any
import types

from fastapi import Response
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from g4f.client.helper import filter_none
from g4f.api.stubs import ChatCompletionsConfig, ImageGenerationConfig
from g4f import debug

from ..config import AppConfig

logger = logging.getLogger(__name__)

class ErrorResponse(Response):
    media_type = "application/json"

    @classmethod
    def from_exception(cls, exception: Exception,
                       config: Union[ChatCompletionsConfig, ImageGenerationConfig] = None,
                       status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
        return cls(format_exception(exception, config), status_code)

    @classmethod
    def from_message(cls, message: str, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR, headers: dict = None):
        return cls(format_exception(message), status_code, headers=headers)

    def render(self, content) -> bytes:
        return str(content).encode(errors="ignore")

def json_default_serializer(obj: Any) -> Any:
    """Custom JSON serializer untuk menangani tipe data kompleks"""
    try:
        # Konversi berbagai tipe data yang tidak bisa di-serialize
        if isinstance(obj, type):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, (types.ModuleType, types.FunctionType, types.MethodType)):
            return str(obj)
        # Tambahkan penanganan tipe data lain yang mungkin tidak bisa di-serialize
        return str(obj)
    except Exception as serialize_error:
        logger.error(f"Cannot serialize object of type {type(obj)}: {serialize_error}")
        return None

def format_exception(e: Union[Exception, str], config: Union[ChatCompletionsConfig, ImageGenerationConfig] = None, image: bool = False) -> str:
    last_provider = {} if not image else debug.get_last_provider(True)
    provider = (AppConfig.media_provider if image else AppConfig.provider)
    model = AppConfig.model
    if config is not None:
        if config.provider is not None:
            provider = config.provider
        if config.model is not None:
            model = config.model
    if isinstance(e, str):
        message = e
    else:
        message = f"{e.__class__.__name__}: {e}"
    return json.dumps({
        "error": {"message": message},
        **filter_none(
            model=last_provider.get("model") if model is None else model,
            provider=last_provider.get("name") if provider is None else provider
        )
    }, default=json_default_serializer)