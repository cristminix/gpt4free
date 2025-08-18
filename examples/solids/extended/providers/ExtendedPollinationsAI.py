import sys
from g4f.Provider import PollinationsAI
from g4f.typing import Messages, AsyncResult, MediaListType
from g4f.Provider.helper import filter_none, format_media_prompt
from g4f.image import is_data_an_audio
from g4f.config import STATIC_URL
from g4f import debug
from g4f.providers.response import ImageResponse, Reasoning, TitleGeneration, SuggestedFollowups
from g4f.requests.raise_for_status import raise_for_status
from g4f.errors import MissingAuthError

from typing import Optional, List, Dict, Any
import random
import asyncio
import json
import os
from datetime import datetime
from aiohttp import ClientSession, ClientTimeout

def transform_messages(messages):
    """
    Transformasi struktur messages untuk menangani konten kompleks
    
    Args:
        messages (list): Daftar pesan yang akan ditransformasi
    
    Returns:
        list: Pesan yang telah ditransformasi
    """
    transformed_messages = []
    
    # Variabel untuk menampung pesan system yang digabungkan
    system_message = None
    
    for message in messages:
        # Tangani pesan system
        # if message['role'] == 'system':
        #     if isinstance(message['content'], list):
        #         # Gabungkan semua konten teks untuk pesan system
        #         system_content = '\n'.join([
        #             item['text'] for item in message['content']
        #             if item['type'] == 'text'
        #         ])
        #         
        #         # Buat atau update pesan system
        #         if system_message is None:
        #             system_message = {
        #                 'role': 'system',
        #                 'content': system_content
        #             }
        #         else:
        #             system_message['content'] += f"\n{system_content}"
        #     else:
        #         # Jika sudah string, langsung gunakan
        #         if system_message is None:
        #             system_message = message
        
        # Tangani pesan user
        # if message['role'] == 'user' or message['role'] == 'system':
        if isinstance(message['content'], list):
            # Buat objek terpisah untuk setiap konten teks
            for item in message['content']:
                if item['type'] == 'text':
                    transformed_messages.append({
                        'role': message['role'],
                        'content': item['text']
                    })
        elif isinstance(message['content'], str):
            # Jika sudah string, langsung tambahkan
            transformed_messages.append({
                'role': message['role'],
                'content': message['content']
            })
    
    # Tambahkan pesan system di awal jika ada
    # if system_message:
    #     transformed_messages.insert(0, system_message)
    
    return transformed_messages

class ExtendedPollinationsAI(PollinationsAI):
    """Extended PollinationsAI provider with additional functionality"""
    
    # Inherit class attributes from the parent class
    # working = True
    # supports_stream = True
    is_extended=True
    
    # # Explicitly define needs_auth attribute to avoid AttributeError
    # needs_auth = False  # or True if the provider requires authentication
    
    # # Explicitly define create_function attribute to avoid AttributeError
    # create_function = PollinationsAI.create_function
    # async_create_function = PollinationsAI.async_create_function
    
    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        stream: bool = True,
        proxy: str = None,
        cache: bool = None,
        referrer: str = STATIC_URL,
        api_key: str = None,
        extra_body: dict = None,
        # Image generation parameters
        prompt: str = None,
        aspect_ratio: str = None,
        width: int = None,
        height: int = None,
        seed: Optional[int] = None,
        nologo: bool = True,
        private: bool = False,
        enhance: bool = None,
        safe: bool = False,
        transparent: bool = False,
        n: int = 1,
        # Text generation parameters
        media: MediaListType = None,
        temperature: float = None,
        presence_penalty: float = None,
        top_p: float = None,
        frequency_penalty: float = None,
        response_format: Optional[dict] = None,
        extra_parameters: list[str] = ["tools", "parallel_tool_calls", "tool_choice", "reasoning_effort", "logit_bias", "voice", "modalities", "audio"],
        **kwargs
    ) -> AsyncResult:
        debug.log(f"HERE2", file=sys.stderr)
        
        if cache is None:
            cache = kwargs.get("action") == "next"
        if extra_body is None:
            extra_body = {}
        if not model:
            has_audio = "audio" in kwargs or "audio" in kwargs.get("modalities", [])
            if not has_audio and media is not None:
                for media_data, filename in media:
                    if is_data_an_audio(media_data, filename):
                        has_audio = True
                        break
            model = cls.default_audio_model if has_audio else model
        elif cls._models_loaded or cls.get_models():
            if model in cls.model_aliases:
                model = cls.model_aliases[model]
        debug.log(f"Using model: {model}")
        if model in cls.image_models:
            async for chunk in cls._generate_image(
                model="gptimage" if model == "transparent" else model,
                prompt=format_media_prompt(messages, prompt),
                media=media,
                proxy=proxy,
                aspect_ratio=aspect_ratio,
                width=width,
                height=height,
                seed=seed,
                cache=cache,
                nologo=nologo,
                private=private,
                enhance=enhance,
                safe=safe,
                transparent=transparent or model == "transparent",
                n=n,
                referrer=referrer,
                api_key=api_key
            ):
                yield chunk
        else:
            if prompt is not None and len(messages) == 1:
                messages = [{
                    "role": "user",
                    "content": prompt
                }]
            if model and model in cls.audio_models[cls.default_audio_model]:
                kwargs["audio"] = {
                    "voice": model,
                }
                model = cls.default_audio_model
            
            # Transform dan simpan messages
            transformed_messages = transform_messages(messages)

            LOG_MESSAGE_TO_FILE=True
            if LOG_MESSAGE_TO_FILE:
                try:
                    # Transform messages sebelum diproses atau disimpan
                    
                    # Tambahkan rutin untuk menyimpan messages ke file JSON
                    log_dir = "examples/logs/request_messages/PollinationsAI"
                    os.makedirs(log_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    log_filename = f"{log_dir}/messages_{timestamp}.json"
                    
                    def custom_json_serializer(obj):
                        try:
                            # Konversi berbagai tipe data yang tidak bisa di-serialize
                            if hasattr(obj, '__dict__'):
                                return obj.__dict__
                            if isinstance(obj, type):
                                return str(obj)
                            # Tambahkan penanganan tipe data lain yang mungkin tidak bisa di-serialize
                            return str(obj)
                        except Exception as serialize_error:
                            debug.log(f"Cannot serialize object of type {type(obj)}: {serialize_error}")
                            return None
                    
                    with open(log_filename, 'w', encoding='utf-8') as log_file:
                        json.dump(transformed_messages, log_file, default=custom_json_serializer, ensure_ascii=False, indent=2)
                except Exception as e:
                    debug.log(f"Error saving messages log: {e}")
            
            async for result in cls._generate_text(
                model=model,
                messages=transformed_messages,
                media=media,
                proxy=proxy,
                temperature=temperature,
                presence_penalty=presence_penalty,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                response_format=response_format,
                seed=seed,
                cache=cache,
                stream=stream,
                extra_parameters=extra_parameters,
                referrer=referrer,
                api_key=api_key,
                extra_body=extra_body,
                **kwargs
            ):
                yield result

# Define needs_auth as a module-level attribute to ensure it's available
# when the module is accessed directly
# needs_auth = ExtendedPollinationsAI.needs_auth

# # Define create_function and async_create_function as module-level attributes
# create_function = ExtendedPollinationsAI.create_function
# async_create_function = ExtendedPollinationsAI.async_create_function

# # Define working as a module-level attribute to ensure it's available
# # when the module is accessed directly
# working = ExtendedPollinationsAI.working
# supports_stream = ExtendedPollinationsAI.supports_stream

# # Define get_dict as a module-level attribute to ensure it's available
# # when the module is accessed directly
# def get_dict():
#     return ExtendedPollinationsAI.get_dict()

# # Also define other attributes that might be accessed directly from the module
# url = ExtendedPollinationsAI.url
# label = getattr(ExtendedPollinationsAI, 'label', None)
# __name__ = ExtendedPollinationsAI.__name__
