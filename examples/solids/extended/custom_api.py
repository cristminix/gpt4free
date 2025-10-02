"""
Custom API with extended functionality.
"""
import sys
import os
import asyncio
import logging
from typing import Iterator, Union
from pathlib import Path as PathLib
from inspect import signature

from flask import Flask, send_from_directory

try:
    from PIL import Image 
    has_pillow = True
except ImportError:
    has_pillow = False

# Add the root directory to the path so we can import g4f modules
root_dir = PathLib(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from g4f.gui.server.api import Api as BaseApi
from g4f.errors import VersionNotFoundError, MissingAuthError
from g4f.image.copy_images import copy_media, ensure_media_dir 
from g4f.image import get_width_height
from g4f.tools.run_tools import iter_run_tools
from g4f import Provider
from g4f.providers.base_provider import ProviderModelMixin
from g4f.providers.retry_provider import BaseRetryProvider
from g4f.providers.helper import format_media_prompt
from g4f.providers.response import *
from g4f import version, models
# from g4f import ChatCompletion, get_model_and_provider
from g4f import debug
from examples.solids.extended.service import get_model_and_provider, convert_to_provider
images_dir = "./generated_images"
media_dir = "./generated_media"
logger = logging.getLogger(__name__)

def get_media_dir() -> str:#
    """Get the directory for storing generated media files"""
    if os.access(images_dir, os.R_OK):
        return images_dir
    return media_dir
class CustomApi(BaseApi):
    """
    Custom API that extends the default API with additional functionality.
    """
    
    def __init__(self, app: Flask) -> None:

        """
        Initialize the custom API.
        """
        # Initialize the base API if needed
        # For static methods, initialization might not be necessary
        pass
    def serve_images_2(self, name):
        ensure_media_dir()
        path=os.path.abspath(get_media_dir())
        # Write the path to a debug file
        with open("debug_path.txt", "w") as f:
            f.write(path)
        return send_from_directory(path, name)

    def _prepare_conversation_kwargs(self, json_data: dict):
        kwargs = {**json_data}
        model = json_data.get('model')
        provider = json_data.get('provider')
        messages = json_data.get('messages')
        action = json_data.get('action')
        if action == "continue":
            kwargs["tool_calls"].append({
                "function": {
                    "name": "continue_tool"
                },
                "type": "function"
            })
        conversation = json_data.get("conversation")
        if isinstance(conversation, dict):
            kwargs["conversation"] = JsonConversation(**conversation)
        return {
            "model": model,
            "provider": provider,
            "messages": messages,
            "ignore_stream": True,
            **kwargs
        }
    def _create_response_stream(self, kwargs: dict, provider: str, download_media: bool = True, tempfiles: list[str] = []) -> Iterator:
        def decorated_log(*values: str, file = None):
            debug.logs.append(" ".join([str(value) for value in values]))
            if debug.logging:
                debug.log_handler(*values, file=file)
        if "user" not in kwargs:
            debug.log = decorated_log
        proxy = os.environ.get("G4F_PROXY")
        provider = kwargs.pop("provider", None)
        try:
            model, provider_handler = get_model_and_provider(
                kwargs.get("model"), provider,
                has_images="media" in kwargs,
            )
            if "user" in kwargs:
                debug.error("User:", kwargs.get("user", "Unknown"))
                debug.error("Referrer:", kwargs.get("referer", ""))
                debug.error("User-Agent:", kwargs.get("user-agent", ""))
        except Exception as e:
            logger.exception(e)
            yield self._format_json('error', type(e).__name__, message=get_error_message(e))
            return
        if not isinstance(provider_handler, BaseRetryProvider):
            if not provider:
                provider = provider_handler.__name__
            yield self.handle_provider(provider_handler, model)
            if hasattr(provider_handler, "get_parameters"):
                yield self._format_json("parameters", provider_handler.get_parameters(as_json=True))
        try:
            result = iter_run_tools(provider_handler, **{**kwargs, "model": model, "download_media": download_media, "proxy": proxy})
            for chunk in result:
                if isinstance(chunk, ProviderInfo):
                    yield self.handle_provider(chunk, model)
                elif isinstance(chunk, JsonConversation):
                    if provider is not None:
                        yield self._format_json("conversation", chunk.get_dict() if provider == "AnyProvider" else {
                            provider: chunk.get_dict()
                        })
                elif isinstance(chunk, Exception):
                    logger.exception(chunk)
                    yield self._format_json('message', get_error_message(chunk), error=type(chunk).__name__)
                elif isinstance(chunk, RequestLogin):
                    yield self._format_json("preview", chunk.to_string())
                elif isinstance(chunk, PreviewResponse):
                    yield self._format_json("preview", chunk.to_string())
                elif isinstance(chunk, ImagePreview):
                    yield self._format_json("preview", chunk.to_string(), urls=chunk.urls, alt=chunk.alt)
                elif isinstance(chunk, MediaResponse):
                    media = chunk
                    if download_media or chunk.get("cookies"):
                        chunk.alt = format_media_prompt(kwargs.get("messages"), chunk.alt)
                        width, height = get_width_height(chunk.get("width"), chunk.get("height"))
                        tags = [model, kwargs.get("aspect_ratio"), kwargs.get("resolution")]
                        media = asyncio.run(copy_media(
                            chunk.get_list(),
                            chunk.get("cookies"),
                            chunk.get("headers"),
                            proxy=proxy,
                            alt=chunk.alt,
                            tags=tags,
                            add_url=True,
                            timeout=kwargs.get("timeout"),
                            return_target=True if isinstance(chunk, ImageResponse) else False,
                        ))
                        options = {}
                        target_paths, urls = get_target_paths_and_urls(media)
                        if target_paths:
                            if has_pillow:
                                try:
                                    with Image.open(target_paths[0]) as img:
                                        width, height = img.size
                                        options = {"width": width, "height": height}
                                except Exception as e:
                                    logger.exception(e)
                            options["target_paths"] = target_paths
                        media = ImageResponse(urls, chunk.alt, options) if isinstance(chunk, ImageResponse) else VideoResponse(media, chunk.alt)
                    yield self._format_json("content", str(media), urls=media.urls, alt=media.alt)
                elif isinstance(chunk, SynthesizeData):
                    yield self._format_json("synthesize", chunk.get_dict())
                elif isinstance(chunk, TitleGeneration):
                    yield self._format_json("title", chunk.title)
                elif isinstance(chunk, RequestLogin):
                    yield self._format_json("login", str(chunk))
                elif isinstance(chunk, Parameters):
                    yield self._format_json("parameters", chunk.get_dict())
                elif isinstance(chunk, FinishReason):
                    yield self._format_json("finish", chunk.get_dict())
                elif isinstance(chunk, Usage):
                    yield self._format_json("usage", chunk.get_dict())
                elif isinstance(chunk, Reasoning):
                    yield self._format_json("reasoning", **chunk.get_dict())
                elif isinstance(chunk, YouTubeResponse):
                    yield self._format_json("content", chunk.to_string())
                elif isinstance(chunk, AudioResponse):
                    yield self._format_json("content", str(chunk), data=chunk.data)
                elif isinstance(chunk, SuggestedFollowups):
                    yield self._format_json("suggestions", chunk.suggestions)
                elif isinstance(chunk, DebugResponse):
                    yield self._format_json("log", chunk.log)
                elif isinstance(chunk, ContinueResponse):
                    yield self._format_json("continue", chunk.log)
                elif isinstance(chunk, RawResponse):
                    yield self._format_json(chunk.type, **chunk.get_dict())
                elif isinstance(chunk, JsonRequest):
                    yield self._format_json("request", chunk.get_dict())
                elif isinstance(chunk, JsonResponse):
                    yield self._format_json("response", chunk.get_dict())
                else:
                    yield self._format_json("content", str(chunk))
        except MissingAuthError as e:
            yield self._format_json('auth', type(e).__name__, message=get_error_message(e))
        except (TimeoutError, asyncio.exceptions.CancelledError) as e:
            if "user" in kwargs:
                debug.error(e, "User:", kwargs.get("user", "Unknown"))
            yield self._format_json('error', type(e).__name__, message=get_error_message(e))
        except Exception as e:
            if "user" in kwargs:
                debug.error(e, "User:", kwargs.get("user", "Unknown"))
            logger.exception(e)
            yield self._format_json('error', type(e).__name__, message=get_error_message(e))
        finally:
            yield from self._yield_logs()
            for tempfile in tempfiles:
                try:
                    os.remove(tempfile)
                except Exception as e:
                    logger.exception(e)
    
    # You can override or add new methods here
    # For example:
    # def get_custom_models(self):
    #     # Add custom logic here
    #     return super().get_models()
    
    # Or add new methods:
    # def get_extended_provider_models(self, provider: str):
    #     # Add custom logic here
    #     return super().get_provider_models(provider)

def get_error_message(exception: Exception) -> str:
    return f"{type(exception).__name__}: {exception}"

def get_target_paths_and_urls(media: list[Union[str, tuple[str, str]]]) -> tuple[list[str], list[str]]:
    target_paths = []
    urls = []
    for item in media:
        if isinstance(item, tuple):
            item, target_path = item
            target_paths.append(target_path)
        urls.append(item)
    return target_paths, urls