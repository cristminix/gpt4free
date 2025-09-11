from examples.solids.extended.providers.lmarenabeta.conversation_json import ConversationJson
from examples.solids.extended.providers.lmarenabeta.data_builder_auto import build_evaluation_data_auto
from g4f.Provider.needs_auth import LMArena
from g4f.Provider.needs_auth.LMArena import click_trunstile,image_models
from g4f.tools.media import merge_media
from g4f.typing import AsyncResult, Messages, MediaListType
from g4f.requests import StreamSession, get_args_from_nodriver, raise_for_status, merge_cookies, has_nodriver
from g4f.errors import ModelNotFoundError, CloudflareError, MissingAuthError
from g4f.providers.response import FinishReason, Usage, JsonConversation, ImageResponse
from g4f.Provider.helper import get_last_user_message
from g4f import debug
import os
import asyncio
import uuid
import json
import requests
try:
    import curl_cffi
    has_curl_cffi = True
except ImportError:
    has_curl_cffi = False

class ExtendedLMArenaBeta(LMArena):
    #https://lmarena.ai/api/stream/post-to-evaluation/b469180b-0fc5-4464-ba54-ba831c573164
    api_endpoint = "https://lmarena.ai/nextjs-api/stream/create-evaluation"

    api_post_endpoint = "https://lmarena.ai/nextjs-api/stream/post-to-evaluation" 
    
    # Inherit class attributes from the parent class
    # working = True
    # supports_stream = True
    is_extended=True
    
    # Add any additional class attributes or methods here
    # def __init__(self):
    #     super().__init__()
        # Initialize any additional attributes
    @classmethod
    def get_models_(cls) -> list[str]:
        if not cls._models_loaded and has_curl_cffi:
            # Define cache file path
            cache_file_path = os.path.join(os.path.dirname(__file__), "lmarena_models_cache.json")
            
            # Check if cache file exists
            if os.path.exists(cache_file_path):
                try:
                    with open(cache_file_path, "r") as f:
                        models_data = json.load(f)
                    cls.text_models = {model["publicName"]: model["id"] for model in models_data if "text" in model["capabilities"]["outputCapabilities"]}
                    cls.image_models = {model["publicName"]: model["id"] for model in models_data if "image" in model["capabilities"]["outputCapabilities"]}
                    cls.vision_models = {model["publicName"] for model in models_data if "image" in model["capabilities"]["inputCapabilities"]}
                    cls.models = list(cls.text_models) + list(cls.image_models)
                    cls.default_model = list(cls.text_models.keys())[0]
                    cls._models_loaded = True
                    return cls.models
                except (json.JSONDecodeError, KeyError, FileNotFoundError):
                    debug.log(f"Cache file {cache_file_path} is corrupted or invalid, removing it.")
                    os.remove(cache_file_path)
            
            # If cache file doesn't exist or was corrupted, proceed with original logic
            cache_file = cls.get_cache_file()
            args = {}
            if cache_file.exists():
                try:
                    with cache_file.open("r") as f:
                        args = json.load(f)
                except json.JSONDecodeError:
                    debug.log(f"Cache file {cache_file} is corrupted, removing it.")
                    cache_file.unlink()
                    args = {}
                if not args:
                    return cls.models
                response = curl_cffi.get(f"{cls.url}/?mode=direct", **args)
                if response.ok:
                    for line in response.text.splitlines():
                        if "initialModels" in line:
                            line = line.split("initialModels", maxsplit=1)[-1].split("initialModelAId")[0][3:-3].replace('\\', '')
                            models = json.loads(line)
                            
                            # Save models data to cache file
                            try:
                                with open(cache_file_path, "w") as f:
                                    json.dump(models, f)
                            except Exception as e:
                                debug.log(f"Failed to save models to cache file: {e}")
                            
                            cls.text_models = {model["publicName"]: model["id"] for model in models if "text" in model["capabilities"]["outputCapabilities"]}
                            cls.image_models = {model["publicName"]: model["id"] for model in models if "image" in model["capabilities"]["outputCapabilities"]}
                            cls.vision_models = {model["publicName"] for model in models if "image" in model["capabilities"]["inputCapabilities"]}
                            cls.models = list(cls.text_models) + list(cls.image_models)
                            cls.default_model = list(cls.text_models.keys())[0]
                            cls._models_loaded = True
                            break
                else:
                    debug.log(f"Failed to load models from {cls.url}: {response.status_code} {response.reason}")
        return cls.models
    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        conversation: JsonConversation = None,
        media: MediaListType = None,
        proxy: str = None,
        timeout: int = None,
        **kwargs
    ) -> AsyncResult:
        debug.log(f"conversation {conversation.get_dict() if conversation else 'None'}")
        # use_conversation_json=False
         

        if cls.share_url is None:
            cls.share_url = os.getenv("G4F_SHARE_URL")
        prompt = get_last_user_message(messages)
        cache_file = cls.get_cache_file()
        args = None
        if cache_file.exists():
            try:
                with cache_file.open("r") as f:
                    args = json.load(f)
            except json.JSONDecodeError:
                debug.log(f"Cache file {cache_file} is corrupted, removing it.")
                cache_file.unlink()
                args = None
        for _ in range(2):
            if args:
                pass
            elif has_nodriver or cls.share_url is None:
                async def callback(page):
                    element = await page.select('[style="display: grid;"]')
                    if element:
                        await click_trunstile(page, 'document.querySelector(\'[style="display: grid;"]\')')
                    await page.find("Ask anything…", 120)
                    button = await page.find("Accept Cookies")
                    if button:
                        await button.click()
                    else:
                        debug.log("No 'Accept Cookies' button found, skipping.")
                    if not await page.evaluate('document.cookie.indexOf("arena-auth-prod-v1") >= 0'):
                        debug.log("No authentication cookie found, trying to authenticate.")
                        await page.select('#cf-turnstile', 300)
                        debug.log("Found Element: 'cf-turnstile'")
                        await asyncio.sleep(3)
                        await click_trunstile(page)
                    while not await page.evaluate('document.cookie.indexOf("arena-auth-prod-v1") >= 0'):
                        await asyncio.sleep(1)
                    while not await page.evaluate('document.querySelector(\'textarea\')'):
                        await asyncio.sleep(1)
                args = await get_args_from_nodriver(cls.url, proxy=proxy, callback=callback)
                with cache_file.open("w") as f:
                    json.dump(args, f)
            elif not cls.looked:
                cls.looked = True
                try:
                    debug.log("No cache file found, trying to fetch from share URL.")
                    response = requests.get(cls.share_url, params={
                        "prompt": prompt,
                        "model": model,
                        "provider": cls.__name__
                    })
                    raise_for_status(response)
                    text, *args = response.text.split("\n" * 10 + "<!--", 1)
                    if args:
                        debug.log("Save args to cache file:", str(cache_file))
                        with cache_file.open("w") as f:
                            f.write(args[0].strip())
                    yield text
                finally:
                    cls.looked = False
                return

            if not cls._models_loaded:
                cls.get_models()
            is_image_model = model in image_models
            if not model:
                model = cls.default_model
            if model in cls.model_aliases:
                model = cls.model_aliases[model]
            if model in cls.text_models:
                model_id = cls.text_models[model]
            elif model in cls.image_models:
                model_id = cls.image_models[model]
            else:
                raise ModelNotFoundError(f"Model '{model}' is not supported by LMArena Beta.")
            
            userMessageId = str(uuid.uuid4())
            modelAMessageId = str(uuid.uuid4())
            evaluationSessionId = str(uuid.uuid4())
            # conversation_json = ConversationJson(evaluationSessionId)
            # use_conversation_json=True
            if not is_image_model:
                data = build_evaluation_data_auto(
                    model_id=model_id,
                    prompt=prompt,
                    userMessageId=userMessageId,
                    modelAMessageId=modelAMessageId,
                    evaluationSessionId=evaluationSessionId,
                    media=media,
                    source_messages=messages,
                    conversation=conversation,
                    is_image_model=is_image_model
                )
            else:
                experimental_attachments = []
                if media and messages:
                    for url, name in list(merge_media(media, messages)):
                        if isinstance(url, str) and url.startswith("https://"):
                            experimental_attachments.append({
                                "name": name or os.path.basename(url) if name is None else name,
                                "contentType": get_content_type(url),
                                "url": url
                            })
                parentMessageIds=[]
                messages = [
                    {
                        "id": userMessageId,
                        "role": "user",
                        "content": prompt,
                        "experimental_attachments": experimental_attachments,
                        "parentMessageIds": [],
                        "participantPosition": "a",
                        "modelId": None,
                        "evaluationSessionId": evaluationSessionId,
                        "status": "pending",
                        "failureReason": None
                    },
                    {
                        "id": modelAMessageId,
                        "role": "assistant",
                        "content": "",
                        "experimental_attachments": [],
                        "parentMessageIds": [userMessageId],
                        "participantPosition": "a",
                        "modelId": model_id,
                        "evaluationSessionId": evaluationSessionId,
                        "status": "pending",
                        "failureReason": None
                    }
                ]
                data = {
                    "id": evaluationSessionId,
                    "mode": "direct",
                    "modelAId": model_id,
                    "userMessageId": userMessageId,
                    "modelAMessageId": modelAMessageId,
                    "messages": messages,
                    "modality": "image" if is_image_model else "chat"
                }
            # exit()
            debug.log(f"using proxy:{proxy}")
            try:
                async with StreamSession(**args, timeout=timeout) as session:
                    # {cls.api_post_endpoint}/{evaluationSessionId}
                    api_endoint = cls.api_endpoint
                    # if use_conversation_json:
                        # if conversation_json.get("continueConversation") == "yes":
                        #     evaluationSessionId=conversation_json.get("evaluationSessionId")
                        #     api_endoint = f"{cls.api_post_endpoint}/{evaluationSessionId}"
                    async with session.post(
                        api_endoint,
                        json=data,
                        proxy=proxy
                    ) as response:
                        await raise_for_status(response)
                        args["cookies"] = merge_cookies(args["cookies"], response)
                        # assistent_messages=""
                        async for chunk in response.iter_lines():
                            line = chunk.decode()
                            # debug.log(f"{line}")

                            if line.startswith("af:"):
                                yield JsonConversation(message_ids=[modelAMessageId])
                            elif line.startswith("a0:"):
                                chunk = json.loads(line[3:])
                                # assistent_messages += chunk
                                if chunk == "hasArenaError":
                                    raise ModelNotFoundError("LMArena Beta encountered an error: hasArenaError")
                                yield chunk
                            elif line.startswith("a2:"):
                                yield ImageResponse([image.get("image") for image in json.loads(line[3:])], prompt)
                            elif line.startswith("ad:"):
                                finish = json.loads(line[3:])
                                if "finishReason" in finish:
                                    # if use_conversation_json:
                                    #     conversation_json.attach_assistant_message(assistent_messages)
                                    #     conversation_json.set("continueConversation","yes")

                                    # debug.log(f"{assistent_messages}")
                                    yield FinishReason(finish["finishReason"])
                                if "usage" in finish:
                                    yield Usage(**finish["usage"])
                break
            except (CloudflareError, MissingAuthError):
                args = None
                debug.log(f"{cls.__name__}: Cloudflare error")
                continue
        if args and os.getenv("G4F_SHARE_AUTH"):
            yield "\n" * 10
            yield "<!--"
            yield json.dumps(args)
        if args:
            debug.log("Save args to cache file:", str(cache_file))
            with cache_file.open("w") as f:
                f.write(json.dumps(args))

def get_content_type(url: str) -> str:
    if url.endswith(".webp"):
        return "image/webp"
    elif url.endswith(".png"):
        return "image/png"
    elif url.endswith(".jpg") or url.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"

# Define working as a module-level attribute to ensure it's available
# when the module is accessed directly
# working = ExtendedLMArenaBeta.working
# supports_stream = ExtendedLMArenaBeta.supports_stream

# # Define get_dict as a module-level attribute to ensure it's available
# # when the module is accessed directly
# def get_dict():
#     return ExtendedLMArenaBeta.get_dict()

# # Also define other attributes that might be accessed directly from the module
# url = ExtendedLMArenaBeta.url
# label = getattr(ExtendedLMArenaBeta, 'label', None)
# __name__ = ExtendedLMArenaBeta.__name__
