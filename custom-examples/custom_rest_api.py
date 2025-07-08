from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional, Union, Tuple
from datetime import datetime
import time
import asyncio
import json
from starlette.responses import StreamingResponse
from qwen_api.client import Qwen
import uuid
from qwen_api.core.exceptions import QwenAPIError
from qwen_api.core.types.chat import ChatMessage as QwenChatMessage, TextBlock, ImageBlock
import base64
import re
from g4f.client import Client
from model_info import MODEL_INFO
import threading
import queue
from pathlib import Path

# ----- Model List -----
overide_model_name = "mixtral-8x22b-instruct-v0.1"
MODEL_NAMES = [
    f"{model['name']}:{provider}"
    for model in MODEL_INFO
    for provider in model["providers"]
]

def get_extension_from_data_url(data_url: str) -> str:
    """Extract file extension from a data URL."""
    match = re.match(r'^data:(?P<mime>[\w/\-\.]+);base64,(?P<data>.+)$', data_url)
    if not match:
        raise ValueError("Invalid data URL format")
    mime_type = match.group('mime')
    mime_to_ext = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/svg+xml': 'svg',
        'text/plain': 'txt',
        'application/pdf': 'pdf',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    }
    extension = mime_to_ext.get(mime_type)
    if not extension:
        raise ValueError(f"Unsupported MIME type: {mime_type}")
    return extension

def create_filename_from_data_url(data_url: str, base_name: str = "file") -> str:
    ext = get_extension_from_data_url(data_url)
    return f"{base_name}.{ext}"

app = FastAPI(title="OpenAI-compatible API")
client = Client()

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List] | None = None
    file: Optional[dict] = None
    web_search: Optional[bool] = None
    thinking: Optional[bool] = False
    web_development: Optional[bool] = True
    blocks: Optional[List[Union[TextBlock, ImageBlock]]] = None

class ChatCompletionRequest(BaseModel):
    model: str = overide_model_name
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False

# ----- Streaming Helper -----
async def _resp_async_generator_stream(response, model):
    q = queue.Queue()
    sentinel = object()
    
    def sync_gen():
        chunk={}
        for i, chunkItem in enumerate(response):
            token = chunkItem.choices[0].delta.content
            if hasattr(chunkItem, "dict"):
                chunkItem = chunkItem.dict()
            chunk = {
                "id": i,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "is_finished": False,
                # "text": token,
                # "model": model,
                "choices": [{"delta": {"content": token}}],
            }
            try:
                # q.put(f"data: {json.dumps(chunk, default=str)}\n")
                q.put(f"data: {json.dumps(chunk, default=str)}\n")
            except Exception as e:
                q.put(f"data: [DONE] {str(e)}\n")
                break
        # chunk["is_finished"] = True
        # chunk["finish_reason"] = "stop"
        # chunk["choices"]=[{"delta": {"content": ""}}]

        q.put("data: [DONE]\n")
        q.put(sentinel)
    threading.Thread(target=sync_gen, daemon=True).start()
    while True:
        item = await asyncio.to_thread(q.get)
        if item is sentinel:
            break
        yield item

def reduce_chat_context(messages: list, keep_first: int = 5, keep_last: int = 10, keep_middle: int = 3):
    n = len(messages)
    if n <= keep_first + keep_middle + keep_last:
        return messages
    start_middle = (n - keep_middle) // 2
    middle_slice = messages[start_middle:start_middle + keep_middle]
    return messages[:keep_first] + middle_slice + messages[-keep_last:]

def generate_model_list():
    now = int(datetime.now().timestamp())
    return [
        {
            "id": name,
            "object": "model",
            "created": now,
            "owned_by": "local"
        }
        for name in MODEL_NAMES
    ]

@app.get("/v1/models")
async def list_models():
    return {
        "data":generate_model_list(),
        "object": "list"
    }

def parse_message_content(message: ChatMessage) -> List[dict]:
    """Parse message content, handle text and image blocks."""
    if isinstance(message.content, list):
        text_content = ""
        file_path = "tmpFile.png"
        getDataImage = None
        for item in message.content:
            if item["type"] == "text":
                text_content = item["text"]
            elif item["type"] == "image_url":
                base64_string = item["image_url"]["url"]
                file_path = create_filename_from_data_url(base64_string, base_name="tmpFile")
                if ',' in base64_string:
                    base64_string = base64_string.split(',')[1]
                Path(file_path).write_bytes(base64.b64decode(base64_string))
                getDataImage = client.chat.upload_file(file_path=file_path)
        if text_content and getDataImage:
            return [ChatMessage(
                role=message.role,
                web_search=False,
                thinking=False,
                web_development=True,
                blocks=[
                    TextBlock(block_type="text", text=text_content),
                    ImageBlock(block_type="image", url=getDataImage.file_url, image_mimetype=getDataImage.image_mimetype)
                ]
            )]
        return []
    else:
        return [{
            "role": message.role,
            "content": message.content,
        }]

def get_name_and_provider(name_provider: str) -> Tuple[str, str]:
    """Given a string in the format 'name:provider', return a tuple (name, provider)."""
    if ':' not in name_provider:
        raise ValueError("Input must be in the format 'name:provider'")
    return tuple(name_provider.split(':', 1))

def build_parsed_messages(request: ChatCompletionRequest) -> list:
    parsed_messages = []
    for message in request.messages:
        parsed_messages.extend(parse_message_content(message))
    return parsed_messages

def generate_response_sync(request: ChatCompletionRequest, useDefaultModel: bool = False):
    parsed_messages = build_parsed_messages(request)
    name, provider = get_name_and_provider(request.model)
    model = name
    response = client.chat.completions.create(
        messages=parsed_messages,
        model=model,
        stream=request.stream,
        temperature=request.temperature,
        provider=provider,
    )
    if request.stream:
        return response
    try:
        return response.choices[0].message
    except Exception as e:
        return ChatMessage(role="assistant", content=f"Error: {e}")

async def generate_response_async(request: ChatCompletionRequest, useDefaultModel: bool = False):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, generate_response_sync, request, useDefaultModel)

@app.post("/v1")
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # request.stream = False
    # print(f"Received request: {request}")
    if request.messages:
        resp_content = await generate_response_async(request)
    else:
        resp_content = ChatMessage(role="assistant", content="As a mock AI Assistant, I can only echo your last message, but there wasn't one!")
    if request.stream:
        # print(f"Streaming response for request: {resp_content}")
        return StreamingResponse(_resp_async_generator_stream(resp_content, request.model), media_type="text/event-stream")
    resp = {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "message": {
                "role": "assistant",
                "content": resp_content.content,
                "tool_calls": getattr(resp_content, "tool_calls", None)
            }
        }]
    }
    # print(f"Returning response: {resp}")
    return resp

