"""
Models-related API routes
"""
import json
from typing import List, Optional

from fastapi import Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)

try:
    from typing import Annotated
except ImportError:
    class Annotated:
        pass

from g4f import Provider, models
from g4f.providers.types import ProviderType
from g4f.providers.any_provider import AnyProvider
from g4f.api.stubs import (
    ModelResponseModel,
    ProviderResponseModel,
    ProviderResponseDetailModel,
    ErrorResponseModel
)

from ..config import AppConfig
from ..utils import get_model_by_providers, blacklisted
from .base import ErrorResponse

async def read_root():
    return RedirectResponse("/v1", 302)

async def read_root_v1():
    return HTMLResponse('g4f API: Go to '
                        '<a href="/v1/models">models xxx</a>, '
                        '<a href="/v1/chat/completions">chat/completions</a>, or '
                        '<a href="/v1/media/generate">media/generate</a> <br><br>'
                        'Open Swagger UI at: '
                        '<a href="/docs">/docs</a>')

async def models_list():
    if True:
        return {
            "object": "list",
            "data": get_model_by_providers()
        }
    else:
        return {
        "object": "list",
        "data": [{
            "id": model,
            "object": "model",
            "created": 0,
            "owned_by": "",
            "image": isinstance(model, models.ImageModel),
            "vision": isinstance(model, models.VisionModel),
            "provider": False,
        } for model in AnyProvider.get_models()] +
        [{
            "id": provider_name,
            "object": "model",
            "created": 0,
            "owned_by": getattr(provider, "label", ""),
            "image": bool(getattr(provider, "image_models", False)),
            "vision": bool(getattr(provider, "vision_models", False)),
            "provider": True,
        } for provider_name, provider in Provider.ProviderUtils.convert.items()
            if provider.working and provider_name not in ("Custom")
        ]
    }

async def provider_models(provider: str, credentials: Annotated[object, Depends(lambda: None)] = None):
    if provider not in Provider.__map__:
        return ErrorResponse.from_message("The provider does not exist.", 404)
    provider: ProviderType = Provider.__map__[provider]
    if not hasattr(provider, "get_models"):
        models_list = []
    elif credentials is not None and hasattr(credentials, "credentials") and credentials.credentials != "secret":
        models_list = provider.get_models(api_key=credentials.credentials)
    else:
        models_list = provider.get_models()
    return {
        "object": "list",
        "data": [{
            "id": model,
            "object": "model",
            "created": 0,
            "owned_by": getattr(provider, "label", provider.__name__),
            "image": model in getattr(provider, "image_models", []),
            "vision": model in getattr(provider, "vision_models", []),
            "audio": model in getattr(provider, "audio_models", []),
            "video": model in getattr(provider, "video_models", []),
            "type": "image" if model in getattr(provider, "image_models", []) else "text",
        } for model in models_list]
    }

async def model_info(model_name: str) -> ModelResponseModel:
    if model_name in models.ModelUtils.convert:
        model_info = models.ModelUtils.convert[model_name]
        return JSONResponse({
            'id': model_name,
            'object': 'model',
            'created': 0,
            'owned_by': model_info.base_provider
        })
    return ErrorResponse.from_message("The model does not exist.", HTTP_404_NOT_FOUND)

async def providers_list():
    return [{
        'id': provider.__name__,
        'object': 'provider',
        'created': 0,
        'url': provider.url,
        'label': getattr(provider, "label", None),
    } for provider in Provider.__providers__ if provider.working]

async def providers_info(provider_name: str):
    if provider_name not in Provider.ProviderUtils.convert:
        return ErrorResponse.from_message("The provider does not exist.", 404)
    provider: ProviderType = Provider.ProviderUtils.convert[provider_name]
    def safe_get_models(provider: ProviderType) -> list[str]:
        try:
            return provider.get_models() if hasattr(provider, "get_models") else []
        except:
            return []
    return {
        'id': provider.__name__,
        'object': 'provider',
        'created': 0,
        'url': provider.url,
        'label': getattr(provider, "label", None),
        'models': safe_get_models(provider),
        'image_models': getattr(provider, "image_models", []) or [],
        'vision_models': [model for model in [getattr(provider, "default_vision_model", None)] if model],
        'params': [*provider.get_parameters()] if hasattr(provider, "get_parameters") else []
    }