"""
Media-related API routes
"""
import json
import os
import base64
import re
import shutil
import asyncio
import hashlib
from types import SimpleNamespace
from email.utils import formatdate
from urllib.parse import quote_plus
from typing import Optional

try:
    from typing import Annotated
except ImportError:
    class Annotated:
        pass

try:
    from PIL import Image 
    has_pillow = True
except ImportError:
    has_pillow = False

from fastapi import Request, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse, Response
from starlette.background import BackgroundTask
from starlette.staticfiles import NotModifiedResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from g4f.client import ImagesResponse
from g4f.client.helper import filter_none
from g4f.image import EXTENSIONS_MAP, is_data_an_media, process_image
from g4f.image.copy_images import get_media_dir, copy_media, get_source_url
from g4f.errors import ProviderNotFoundError, ModelNotFoundError, MissingAuthError
from g4f.providers.response import AudioResponse
from g4f.api.stubs import (
    ImageGenerationConfig,
    TranscriptionResponseModel,
    AudioSpeechConfig,
    FileResponseModel
)

from ..config import AppConfig
from .base import ErrorResponse

async def generate_image(
    request: Request,
    config: ImageGenerationConfig,
    provider: str = None,
    credentials: Annotated[object, Depends(lambda: None)] = None,
    api_client=None
):
    if config.provider is None:
        config.provider = provider
    if config.provider is None:
        config.provider = AppConfig.media_provider
    if config.api_key is None and credentials is not None and hasattr(credentials, "credentials") and credentials.credentials != "secret":
        config.api_key = credentials.credentials
    try:
        response = await api_client.images.generate(
            **config.dict(exclude_none=True),
        )
        for image in response.data:
            if hasattr(image, "url") and image.url.startswith("/"):
                image.url = f"{request.base_url}{image.url.lstrip('/')}"
        return response
    except (ModelNotFoundError, ProviderNotFoundError) as e:
        return ErrorResponse.from_exception(e, config, HTTP_404_NOT_FOUND)
    except MissingAuthError as e:
        return ErrorResponse.from_exception(e, config, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return ErrorResponse.from_exception(e, config, HTTP_500_INTERNAL_SERVER_ERROR)

async def convert(
    file: UploadFile,
    path_provider: str = None,
    model: Annotated[Optional[str], Form()] = None,
    provider: Annotated[Optional[str], Form()] = None,
    prompt: Annotated[Optional[str], Form()] = "Transcribe this audio",
    api_client=None
):
    provider = provider if path_provider is None else path_provider
    kwargs = {"modalities": ["text"]}
    if provider == "MarkItDown":
        kwargs = {
            "llm_client": api_client,
        }
    try:
        response = await api_client.chat.completions.create(
            messages=prompt,
            model=model,
            provider=provider,
            media=[[file.file, file.filename]],
            **kwargs
        )
        return {"text": response.choices[0].message.content, "model": response.model, "provider": response.provider}
    except (ModelNotFoundError, ProviderNotFoundError) as e:
        return ErrorResponse.from_exception(e, None, HTTP_404_NOT_FOUND)
    except MissingAuthError as e:
        return ErrorResponse.from_exception(e, None, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return ErrorResponse.from_exception(e, None, HTTP_500_INTERNAL_SERVER_ERROR)

async def markitdown(
    file: UploadFile,
    api_client=None
):
    return await convert(file, "MarkItDown", api_client=api_client)

async def generate_speech(
    config: AudioSpeechConfig,
    provider: str = AppConfig.media_provider,
    credentials: Annotated[object, Depends(lambda: None)] = None,
    api_client=None
):
    api_key = None
    if credentials is not None and hasattr(credentials, "credentials") and credentials.credentials != "secret":
        api_key = credentials.credentials
    try:
        audio = filter_none(voice=config.voice, format=config.response_format, language=config.language)
        response = await api_client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"{config.instrcutions} Text: {config.input}"}
            ],
            model=config.model,
            provider=config.provider if provider is None else provider,
            prompt=config.input,
            api_key=api_key,
            download_media=config.download_media,
            **filter_none(
                audio=audio if audio else None,
            )
        )
        if response.choices[0].message.audio is not None:
            response_data = base64.b64decode(response.choices[0].message.audio.data)
            return Response(response_data, media_type=f"audio/{config.response_format.replace('mp3', 'mpeg')}")
        elif isinstance(response.choices[0].message.content, AudioResponse):
            response_data = response.choices[0].message.content.data
            response_data = response_data.replace("/media", get_media_dir())
            def delete_file():
                try:
                    os.remove(response_data)
                except Exception as e:
                    print(f"Error deleting file: {e}")
            return FileResponse(response_data, background=BackgroundTask(delete_file))
    except (ModelNotFoundError, ProviderNotFoundError) as e:
        return ErrorResponse.from_exception(e, None, HTTP_404_NOT_FOUND)
    except MissingAuthError as e:
        return ErrorResponse.from_exception(e, None, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return ErrorResponse.from_exception(e, None, HTTP_500_INTERNAL_SERVER_ERROR)

def upload_cookies(
    files: list[UploadFile],
    credentials: Annotated[object, Depends(lambda: None)] = None,
):
    from g4f.cookies import read_cookie_files, get_cookies_dir
    
    response_data = []
    if not AppConfig.ignore_cookie_files:
        for file in files:
            try:
                if file and file.filename.endswith(".json") or file.filename.endswith(".har"):
                    filename = os.path.basename(file.filename)
                    with open(os.path.join(get_cookies_dir(), filename), 'wb') as f:
                        shutil.copyfileobj(file.file, f)
                    response_data.append({"filename": filename})
            finally:
                file.file.close()
        read_cookie_files()
    return response_data

async def get_json(filename, request: Request):
    await asyncio.sleep(30)
    return ""

def get_timestamp(str):
    m = re.match("^[0-9]+", str)
    if m:
        return int(m.group(0))
    else:
        return 0

async def get_media(filename, request: Request, thumbnail: bool = False):
    from g4f.image.copy_images import get_media_dir
    
    target = os.path.join(get_media_dir(), os.path.basename(filename))
    if thumbnail and has_pillow:
        thumbnail_dir = os.path.join(get_media_dir(), "thumbnails")
        thumbnail_path = os.path.join(thumbnail_dir, filename)
    if not os.path.isfile(target):
        other_name = os.path.join(get_media_dir(), os.path.basename(quote_plus(filename)))
        if os.path.isfile(other_name):
            target = other_name
    ext = os.path.splitext(filename)[1][1:]
    mime_type = EXTENSIONS_MAP.get(ext)
    stat_result = SimpleNamespace()
    stat_result.st_size = 0
    stat_result.st_mtime = get_timestamp(filename)
    if thumbnail and has_pillow and os.path.isfile(thumbnail_path):
        stat_result.st_size = os.stat(thumbnail_path).st_size
    elif not thumbnail and os.path.isfile(target):
        stat_result.st_size = os.stat(target).st_size
    headers = {
        "cache-control": "public, max-age=31536000",
        "last-modified": formatdate(stat_result.st_mtime, usegmt=True),
        "etag": f'"{hashlib.md5(filename.encode()).hexdigest()}"',
        **({
            "content-length": str(stat_result.st_size),
        } if stat_result.st_size else {}),
        **({} if thumbnail or mime_type is None else {
            "content-type": mime_type,
        })
    }
    try:
        if_none_match = request.headers["if-none-match"]
        etag = headers["etag"]
        if etag in [tag.strip(" W/") for tag in if_none_match.split(",")]:
            return NotModifiedResponse(headers)
    except KeyError:
        pass
    if not os.path.isfile(target) and mime_type is not None:
        source_url = get_source_url(str(request.query_params))
        ssl = None
        if source_url is None:
            backend_url = os.environ.get("G4F_BACKEND_URL")
            if backend_url:
                source_url = f"{backend_url}/media/{filename}"
                ssl = False
        if source_url is not None:
            try:
                await copy_media(
                    [source_url],
                    target=target, ssl=ssl)
            except Exception as e:
                return RedirectResponse(url=source_url)
    if thumbnail and has_pillow:
        try:
            if not os.path.isfile(thumbnail_path):
                image = Image.open(target)
                os.makedirs(thumbnail_dir, exist_ok=True)
                process_image(image, save=thumbnail_path)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    if thumbnail and os.path.isfile(thumbnail_path):
        result = thumbnail_path
    else:
        result = target
    if not os.path.isfile(result):
        return ErrorResponse.from_message("File not found", HTTP_404_NOT_FOUND)
    async def stream():
        with open(result, "rb") as file:
            while True:
                chunk = file.read(65536)
                if not chunk:
                    break
                yield chunk
    return StreamingResponse(stream(), headers=headers)

async def get_media_thumbnail(filename: str, request: Request):
    return await get_media(filename, request, True)