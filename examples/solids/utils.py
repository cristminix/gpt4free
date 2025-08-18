"""
Utility functions module
"""
import os
import json
from contextlib import asynccontextmanager

from fastapi import Request

from g4f import Provider
from g4f.cookies import read_cookie_files, get_cookies_dir

try:
    from nodriver import util
    has_nodriver = True
except ImportError:
    has_nodriver = False

try:
    from g4f.gui.server.crypto import create_or_read_keys, decrypt_data, get_session_key
    has_crypto = True
except ImportError:
    has_crypto = False

try:
    from PIL import Image 
    has_pillow = True
except ImportError:
    has_pillow = False

from .config import AppConfig

blacklisted = ["AnyProvider", "OpenRouter", "OpenRouterFree", "FenayAI", "Ollama", "BlackboxPro", "Anthropic", "Azure"]

def get_name_and_provider(name_provider: str) -> tuple[str, str]:
    """Given a string in the format 'name:provider', return a tuple (name, provider)."""
    if ':' not in name_provider:
        return tuple("openai:PollinationsAI".split(':', 1))
    return tuple(name_provider.split(':', 1))

def update_headers(request: Request, user: str) -> Request:
    new_headers = request.headers.mutablecopy()
    del new_headers["Authorization"]
    if user:
        new_headers["x-user"] = user
    request.scope["headers"] = new_headers.raw
    delattr(request, "_headers")
    return request

@asynccontextmanager
async def lifespan(app):
    # Read cookie files if not ignored
    if not AppConfig.ignore_cookie_files:
        read_cookie_files()
    AppConfig.g4f_api_key = os.environ.get("G4F_API_KEY", AppConfig.g4f_api_key)
    yield
    if has_nodriver:
        for browser in util.get_registered_instances():
            if browser.connection:
                browser.stop()
        lock_file = os.path.join(get_cookies_dir(), ".nodriver_is_open")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception as e:
                print(f"Failed to remove lock file {lock_file}:", e)

def get_model_by_providers():
    output_dir = "examples/provider_models"

    model_by_providers = []
    for provider_name, provider in Provider.ProviderUtils.convert.items():
        if provider_name in blacklisted:
            continue
        filename = os.path.join(output_dir, f"{provider_name}.json")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                models = json.load(f)
        else:
            models = []
        for model in models:
            try:
                model_name = model.get("model", model.get("label", "unknown_model"))
                model_by_providers.append({
                    "id": f"{model_name}:{provider_name}",
                    "object": "model",
                    "created": 0,
                    "owned_by": "",
                    "image": model.get("image", False),
                    "vision": model.get("vision", False),
                    "provider": provider_name,
                })
            except Exception as e:
                print(f"Error processing model for {provider_name}: {str(e)}")
                pass
    return model_by_providers