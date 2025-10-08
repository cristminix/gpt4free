"""
Chat completions API routes
"""
import json
from typing import List, Optional

from examples.solids.extended.providers import ExtendedGLM
from g4f import debug

# Enable debug logging
debug.enable_logging()

try:
    from typing import Annotated
except ImportError:
    class Annotated:
        pass

from fastapi import Request, Depends, Header
from fastapi.responses import StreamingResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from g4f.client import ChatCompletion, ClientResponse
from g4f.providers.response import BaseConversation, JsonConversation
from g4f.client.helper import filter_none
from g4f.image import is_data_an_media
from g4f.errors import ProviderNotFoundError, ModelNotFoundError, MissingAuthError, NoValidHarFileError
from ..stubs import (
    ChatCompletionsConfig,
    ResponsesConfig,
    ErrorResponseModel
)

from ..config import AppConfig
from ..utils import get_name_and_provider
from .base import ErrorResponse
from examples.solids.extended.providers.ExtendedPollinationsAI import ExtendedPollinationsAI
from examples.solids.extended.providers.ExtendedBlackbox import ExtendedBlackbox
from examples.solids.extended.providers.ExtendedLMArenaBeta import ExtendedLMArenaBeta

async def chat_completions(
    config: ChatCompletionsConfig,
    credentials: Annotated[object, Depends(lambda: None)] = None,
    provider: str = None,
    conversation_id: str = None,
    x_user: Annotated[str | None, Header()] = None,
    api_client=None,
    conversations=None
):
    try:
        # debug.log(config)
        if config.provider is None:
            config.provider = AppConfig.provider if provider is None else provider
        if config.conversation_id is None:
            config.conversation_id = conversation_id
        if config.timeout is None:
            config.timeout = AppConfig.timeout
        if credentials is not None and hasattr(credentials, "credentials") and credentials.credentials != "secret":
            config.api_key = credentials.credentials

        conversation = config.conversation
        if conversation:
            conversation = JsonConversation(**conversation)
        elif config.conversation_id is not None and config.provider is not None:
            if config.conversation_id in conversations:
                if config.provider in conversations[config.conversation_id]:
                    conversation = conversations[config.conversation_id][config.provider]

        if config.image is not None:
            try:
                is_data_an_media(config.image)
            except ValueError as e:
                return ErrorResponse.from_message(f"The image you send must be a data URI. Example: data:image/jpeg;base64,...", status_code=HTTP_422_UNPROCESSABLE_ENTITY)
        if config.media is None:
            config.media = config.images
        if config.media is not None:
            for image in config.media:
                try:
                    is_data_an_media(image[0], image[1])
                except ValueError as e:
                    example = json.dumps({"media": [["data:image/jpeg;base64,...", "filename.jpg"]]})
                    return ErrorResponse.from_message(f'The media you send must be a data URIs. Example: {example}', status_code=HTTP_422_UNPROCESSABLE_ENTITY)

        # Create the completion response
        if True:
            name, provider = get_name_and_provider(config.model)
            # if provider == "PollinationsAI" :
            #     provider = ExtendedPollinationsAI
            # elif provider == "Balackbox":
            #     provider = ExtendedBlackbox
            if provider == "LMArenaBeta":
                provider = ExtendedLMArenaBeta
            elif provider == "LMArena":
                provider = ExtendedLMArenaBeta
            elif provider == "GLM":
                provider = ExtendedGLM
            config.provider = provider
            config.model = name
           
            debug.log(f"Using {config.model}")
            response = api_client.chat.completions.create(
                **filter_none(
                    **{
                        "model": name,
                        "provider": provider,
                        "proxy": AppConfig.proxy,
                        **config.dict(exclude_none=True),
                        **{
                            "conversation_id": None,
                            "conversation": conversation
                        }
                    },
                    # ignored=AppConfig.ignored_providers
                ),
            )
        else:
            response = api_client.chat.completions.create(
                **filter_none(
                    **{
                        "model": AppConfig.model,
                        "provider": AppConfig.provider,
                        "proxy": AppConfig.proxy,
                        **config.dict(exclude_none=True),
                        **{
                            "conversation_id": None,
                            "conversation": conversation,
                            "user": x_user,
                        }
                    },
                    ignored=AppConfig.ignored_providers
                ),
            )

        if not config.stream:
            return await response

        async def streaming():
            try:
                async for chunk in response:
                    if isinstance(chunk, BaseConversation):
                        if config.conversation_id is not None and config.provider is not None:
                            if config.conversation_id not in conversations:
                                conversations[config.conversation_id] = {}
                            conversations[config.conversation_id][config.provider] = chunk
                    else:
                        yield f"data: {chunk.json()}\n\n"
            except GeneratorExit:
                pass
            except Exception as e:
                yield f'data: {ErrorResponse.from_exception(e, config)}\n\n'
            yield "data: [DONE]\n\n"

        return StreamingResponse(streaming(), media_type="text/event-stream")

    except (ModelNotFoundError, ProviderNotFoundError) as e:
        return ErrorResponse.from_exception(e, config, HTTP_404_NOT_FOUND)
    except (MissingAuthError, NoValidHarFileError) as e:
        return ErrorResponse.from_exception(e, config, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return ErrorResponse.from_exception(e, config, HTTP_500_INTERNAL_SERVER_ERROR)

async def v1_responses(
    config: ResponsesConfig,
    credentials: Annotated[object, Depends(lambda: None)] = None,
    provider: str = None,
    api_client=None
):
    try:
        if config.provider is None:
            config.provider = AppConfig.provider if provider is None else provider
        if config.api_key is None and credentials is not None and hasattr(credentials, "credentials") and credentials.credentials != "secret":
            config.api_key = credentials.credentials

        conversation = None
        if config.conversation is not None:
            conversation = JsonConversation(**config.conversation)

        return await api_client.responses.create(
            **filter_none(
                **{
                    "model": AppConfig.model,
                    "proxy": AppConfig.proxy,
                    **config.dict(exclude_none=True),
                    "conversation": conversation
                },
                ignored=AppConfig.ignored_providers
            ),
        )
    except (ModelNotFoundError, ProviderNotFoundError) as e:
        return ErrorResponse.from_exception(e, config, HTTP_404_NOT_FOUND)
    except (MissingAuthError, NoValidHarFileError) as e:
        return ErrorResponse.from_exception(e, config, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return ErrorResponse.from_exception(e, config, HTTP_500_INTERNAL_SERVER_ERROR)