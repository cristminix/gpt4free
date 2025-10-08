from g4f.Provider.GLM import GLM
from g4f.typing import AsyncResult, Messages
from g4f.providers.response import Usage, Reasoning
from g4f.requests import StreamSession, raise_for_status
from g4f import debug
# from __future__ import annotations

import uuid
import requests
class ExtendedGLM(GLM):
    """
    ExtendedGLM provider class that extends the GLM base class
    to implement extended functionality for the API.
    """
    url = "https://chat.z.ai"
    api_endpoint = "https://chat.z.ai/api/chat/completions"
    working = True
    active_by_default = True
    default_model = "GLM-4.5"
    api_key = None

    @classmethod
    def create_signature_with_timestamp(cls,e: str, t: str):
        import time
        import hashlib
        import hmac
        
        current_time = int(time.time() * 1000)  # Current time in milliseconds
        current_time_string = str(current_time)
        data_string = f"{e}|{t}|{current_time_string}"
        time_window = current_time // (5 * 60 * 1000)  # 5 minutes in milliseconds
        
        base_signature = hmac.new(
            "junjie".encode("utf-8"),
            str(time_window).encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        signature = hmac.new(
            base_signature.encode("utf-8"),
            data_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "signature": signature,
            "timestamp": current_time
        }

    @classmethod
    def prepare_auth_params(cls, token: str, user_id: str):
        import time
        import urllib.parse
        
        # Basic parameters
        current_time = str(int(time.time() * 1000))
        request_id = str(uuid.uuid1())  # Using uuid1 which is equivalent to v1
        
        basic_params = {
            "timestamp": current_time,
            "requestId": request_id,
            "user_id": user_id,
        }
        
        # Additional parameters
        additional_params = {
            "version": "0.0.1",
            "platform": "web",
            "token": token,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "language": "en-US",
            "languages": "en-US,en",
            "timezone": "Asia/Jakarta",
            "cookie_enabled": "true",
            "screen_width": "1920",
            "screen_height": "1080",
            "screen_resolution": "1920x1080",
            "viewport_height": "900",
            "viewport_width": "1440",
            "viewport_size": "1440x900",
            "color_depth": "24",
            "pixel_ratio": "1",
            "current_url": "https://chat.z.ai/c/e1295904-98d3-4d85-b6ee-a211471101e9",
            "pathname": "/",
            "search": "",
            "hash": "",
            "host": "z.ai",
            "hostname": "chat.z.ai",
            "protocol": "https",
            "referrer": "https://accounts.google.com/",
            "title": "A Little House Keeping",
            "timezone_offset": str(-(time.timezone if time.daylight == 0 else time.altzone) // 60),
            "local_time": time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime()),
            "utc_time": time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
            "is_mobile": "false",
            "is_touch": "false",
            "max_touch_points": "5",
            "browser_name": "Chrome",
            "os_name": "Linux",
        }
        
        # Combine parameters
        all_params = {**basic_params, **additional_params}
        
        # Create URLSearchParams equivalent
        url_params_string = urllib.parse.urlencode(all_params)
        
        # Create sorted payload (basic params only, sorted by key)
        sorted_payload = ','.join([f"{k},{v}" for k, v in sorted(basic_params.items())])
        
        return {
            "sortedPayload": sorted_payload,
            "urlParams": url_params_string
        }
    
    @classmethod
    def get_endpoint_signature(cls, token: str, user_id: str, user_prompt: str):
        # Get auth parameters
        auth_params = cls.prepare_auth_params(token, user_id)
        sorted_payload = auth_params["sortedPayload"]
        url_params = auth_params["urlParams"]
        
        debug.log(f"Prompt:{user_prompt}")
        last_user_prompt = user_prompt.strip()
        
        # Create signature with timestamp
        signature_data = cls.create_signature_with_timestamp(sorted_payload, last_user_prompt)
        signature = signature_data["signature"]
        timestamp = signature_data["timestamp"]
        
        # Construct the endpoint URL
        endpoint = f"{cls.api_endpoint}?{url_params}&signature_timestamp={timestamp}"
        
        return (endpoint, signature, timestamp)
         
    @classmethod
    def get_models(cls, **kwargs) -> str:
        if not cls.models:
            try:
                response = requests.get(f"{cls.url}/api/v1/auths/")
                debug.log(f"GLM auth response: {response.status_code}")
                response.raise_for_status()
                response_json = response.json()
                cls.api_key = response_json.get("token")
                debug.log(response_json)
                debug.log(f"GLM auth response: {response.status_code}")

                response = requests.get(f"{cls.url}/api/models", headers={"Authorization": f"Bearer {cls.api_key}"})
                response.raise_for_status()
                data = response.json().get("data", [])

                cls.model_aliases = {item.get("name", "").replace("\u4efb\u52a1\u4e13\u7528", "ChatGLM"): item.get("id") for item in data}
                cls.models = list(cls.model_aliases.keys())
                debug.log(cls.models)
                debug.log(cls.model_aliases)

            except requests.RequestException as e:
                debug.log(f"Error fetching GLM models: {e}")
                # Return default models if available, or empty list
                if not cls.models:
                    cls.models = [cls.default_model] if cls.default_model else []
        return cls.models
    @classmethod
    def transform_messages(cls,messages):
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
        
        return transformed_messages
    
    @classmethod
    def get_last_user_message_content(cls, messages):
        """
        Get the content of the last message with role 'user'
        
        Args:
            messages (list): List of message objects with 'role' and 'content' properties
        
        Returns:
            str: Content of the last user message, or None if no user message is found
        """
        # Iterate through messages in reverse order to find the last user message
        for message in reversed(messages):
            if message.get('role') == 'user':
                return message.get('content')
        # Return None if no user message is found
        return None
    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        proxy: str = None,
        **kwargs
    ) -> AsyncResult:
        cls.get_models()
        try:
            model = cls.get_model(model)
        except Exception:
            # If get_model fails, use the provided model directly
            model = model
        
        # Ensure we have an API key before proceeding
        if not cls.api_key:
            raise Exception("Failed to obtain API key from authentication endpoint")
        transformed_messages = cls.transform_messages(messages)
        user_prompt= cls.get_last_user_message_content(transformed_messages)
        debug.log(f"user_prompt:{user_prompt}")
        endpoint, signature, timestamp = cls.get_endpoint_signature(cls.api_key,uuid.uuid4(),user_prompt)    
        data = {
            "chat_id": "local",
            "id": str(uuid.uuid4()),
            "stream": True,
            "model": model,
            "messages": transformed_messages,
            "params": {},
            "tool_servers": [],
            "features": {
                "enable_thinking": True
            }
        }
        async with StreamSession(
            impersonate="chrome",
            proxy=proxy,
        ) as session:
            async with session.post(
                endpoint,
                json=data,
                headers={
                    "Authorization": f"Bearer {cls.api_key}",
                      "x-fe-version": "prod-fe-1.0.95",
                      #028eaf95b163bfa413710c2ab762b722dec75e28ea899a2bdad4ce356e9eac68
                      "x-signature": signature
                },
            ) as response:
                await raise_for_status(response)
                usage = None
                async for chunk in response.sse():
                    if chunk.get("type") == "chat:completion":
                        if not usage:
                            usage = chunk.get("data", {}).get("usage")
                            if usage:
                                yield Usage(**usage)
                        if chunk.get("data", {}).get("phase") == "thinking":
                            delta_content = chunk.get("data", {}).get("delta_content")
                            delta_content = delta_content.split("</summary>\n>")[-1] if delta_content else ""
                            if delta_content:
                                yield Reasoning(delta_content)
                        else:
                            edit_content = chunk.get("data", {}).get("edit_content")
                            if edit_content:
                                yield edit_content.split("\n</details>\n")[-1]
                            else:
                                delta_content = chunk.get("data", {}).get("delta_content")
                                if delta_content:
                                    yield delta_content