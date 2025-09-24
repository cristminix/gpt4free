"""
API main class module - Coordinator that registers all routes
"""
from typing import List, Optional
from fastapi import FastAPI, Request, UploadFile, Form, Header, Depends
from fastapi.responses import RedirectResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_422_UNPROCESSABLE_ENTITY, 
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

try:
    from typing import Annotated
except ImportError:
    class Annotated:
        pass

from examples.solids.api.utils import get_messages
from g4f import debug
debug.enable_logging()
from g4f.client import ChatCompletion, ClientResponse, ImagesResponse
from ..stubs import (
    ChatCompletionsConfig, ImageGenerationConfig,
    ProviderResponseModel, ModelResponseModel,
    ErrorResponseModel, ProviderResponseDetailModel,
    FileResponseModel,
    TranscriptionResponseModel, AudioSpeechConfig,
    ResponsesConfig
)

from ..config import AppConfig
from .core import Api
from .base import ErrorResponse
from .models import (
    read_root, read_root_v1, models_list, provider_models, 
    model_info, providers_list, providers_info
)
from .chat import chat_completions, v1_responses
from .media import (
    generate_image, convert, markitdown, generate_speech,
    upload_cookies, get_json, get_media, get_media_thumbnail
)

async def modify_request_config(source_config):
    source_config.messages = await get_messages(source_config.messages)
    return source_config
def register_routes(api_instance):
    """Register all API routes"""
    if not AppConfig.gui:
        @api_instance.app.get("/")
        async def read_root_endpoint():
            return await read_root()

    @api_instance.app.get("/v1")
    async def read_root_v1_endpoint():
        return await read_root_v1()

    @api_instance.app.get("/v1/models", responses={
        HTTP_200_OK: {"model": List[ModelResponseModel]},
    })
    async def models_endpoint():
        return await models_list()

    @api_instance.app.get("/api/{provider}/models", responses={
        HTTP_200_OK: {"model": List[ModelResponseModel]},
    })
    async def provider_models_endpoint(provider: str, credentials: Annotated[object, Depends(Api.security)] = None):
        return await provider_models(provider, credentials)

    @api_instance.app.get("/v1/models/{model_name}", responses={
        HTTP_200_OK: {"model": ModelResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
    })
    @api_instance.app.post("/v1/models/{model_name}", responses={
        HTTP_200_OK: {"model": ModelResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
    })
    async def model_info_endpoint(model_name: str) -> ModelResponseModel:
        return await model_info(model_name)

    responses = {
        HTTP_200_OK: {"model": ChatCompletion},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
        HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponseModel},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseModel},
    }
    @api_instance.app.post("/v1/chat/completions", responses=responses)
    @api_instance.app.post("/api/{provider}/chat/completions", responses=responses)
    @api_instance.app.post("/api/{provider}/{conversation_id}/chat/completions", responses=responses)
    async def chat_completions_endpoint(
        config: ChatCompletionsConfig,
        credentials: Annotated[object, Depends(Api.security)] = None,
        provider: str = None,
        conversation_id: str = None,
        x_user: Annotated[str | None, Header()] = None,
        
    ):
        # debug.log(config)
        modified_config=await modify_request_config(config)
        return await chat_completions(modified_config, credentials, provider, conversation_id, x_user, api_instance.client, api_instance.conversations)

    responses = {
        HTTP_200_OK: {"model": ClientResponse},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
        # HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponseModel},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseModel},
    }
    @api_instance.app.post("/v1/responses", responses=responses)
    async def v1_responses_endpoint(
        config: ResponsesConfig,
        credentials: Annotated[object, Depends(Api.security)] = None,
        provider: str = None
    ):
        return await v1_responses(config, credentials, provider, api_instance.client)

    @api_instance.app.post("/api/{provider}/responses", responses=responses)
    async def provider_responses_endpoint(
        provider: str,
        config: ChatCompletionsConfig,
        credentials: Annotated[object, Depends(Api.security)] = None,
    ):
        return await v1_responses(config, credentials, provider, api_instance.client)

    responses = {
        HTTP_200_OK: {"model": ImagesResponse},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseModel},
    }
    @api_instance.app.post("/v1/media/generate", responses=responses)
    @api_instance.app.post("/v1/images/generate", responses=responses)
    @api_instance.app.post("/v1/images/generations", responses=responses)
    @api_instance.app.post("/api/{provider}/images/generations", responses=responses)
    async def generate_image_endpoint(
        request: Request,
        config: ImageGenerationConfig,
        provider: str = None,
        credentials: Annotated[object, Depends(Api.security)] = None
    ):
        return await generate_image(request, config, provider, credentials, api_instance.client)

    @api_instance.app.get("/v1/providers", responses={
        HTTP_200_OK: {"model": List[ProviderResponseModel]},
    })
    async def providers_endpoint():
        return await providers_list()

    @api_instance.app.get("/v1/providers/{provider}", responses={
        HTTP_200_OK: {"model": ProviderResponseDetailModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
    })
    async def providers_info_endpoint(provider: str):
        return await providers_info(provider)

    responses = {
        HTTP_200_OK: {"model": TranscriptionResponseModel},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseModel},
    }
    @api_instance.app.post("/v1/audio/transcriptions", responses=responses)
    @api_instance.app.post("/api/{path_provider}/audio/transcriptions", responses=responses)
    async def convert_endpoint(
        file: UploadFile,
        path_provider: str = None,
        model: Annotated[Optional[str], Form()] = None,
        provider: Annotated[Optional[str], Form()] = None,
        prompt: Annotated[Optional[str], Form()] = "Transcribe this audio"
    ):
        return await convert(file, path_provider, model, provider, prompt, api_instance.client)

    @api_instance.app.post("/api/markitdown", responses=responses)
    async def markitdown_endpoint(
        file: UploadFile
    ):
        return await markitdown(file, api_instance.client)

    responses = {
        HTTP_200_OK: {"content": {"audio/*": {}}},
        HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        HTTP_404_NOT_FOUND: {"model": ErrorResponseModel},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseModel},
    }
    @api_instance.app.post("/v1/audio/speech", responses=responses)
    @api_instance.app.post("/api/{provider}/audio/speech", responses=responses)
    async def generate_speech_endpoint(
        config: AudioSpeechConfig,
        provider: str = AppConfig.media_provider,
        credentials: Annotated[object, Depends(Api.security)] = None
    ):
        return await generate_speech(config, provider, credentials, api_instance.client)

    @api_instance.app.post("/v1/upload_cookies", responses={
        HTTP_200_OK: {"model": List[FileResponseModel]},
    })
    def upload_cookies_endpoint(
        files: list[UploadFile],
        credentials: Annotated[object, Depends(Api.security)] = None
    ):
        return upload_cookies(files, credentials)

    @api_instance.app.post("/json/{filename}")
    async def get_json_endpoint(filename, request: Request):
        return await get_json(filename, request)

    @api_instance.app.get("/images/{filename}", responses={
        HTTP_200_OK: {"content": {"image/*": {}}},
        HTTP_404_NOT_FOUND: {}
    })
    @api_instance.app.get("/media/{filename}", responses={
        HTTP_200_OK: {"content": {"image/*": {}, "audio/*": {}}, "video/*": {}},
        HTTP_404_NOT_FOUND: {}
    })
    async def get_media_endpoint(filename, request: Request, thumbnail: bool = False):
        debug.log(filename)
        return await get_media(filename, request, thumbnail)

    @api_instance.app.get("/thumbnail/{filename}", responses={
        HTTP_200_OK: {"content": {"image/*": {}, "audio/*": {}}, "video/*": {}},
        HTTP_404_NOT_FOUND: {}
    })
    async def get_media_thumbnail_endpoint(filename: str, request: Request):
        return await get_media_thumbnail(filename, request)