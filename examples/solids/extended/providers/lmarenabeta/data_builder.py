"""
Data builder utilities for LMArena Beta provider.
"""
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Any
import uuid
from examples.solids.extended.providers.lmarenabeta.conversation_json import ConversationJson
from g4f import debug
from g4f.typing import Messages, MediaListType
from g4f.tools.media import merge_media
from g4f.providers.response import FinishReason, Usage, JsonConversation, ImageResponse


def get_content_type(url: str) -> str:
    """Determine content type based on file extension."""
    if url.endswith(".webp"):
        return "image/webp"
    elif url.endswith(".png"):
        return "image/png"
    elif url.endswith(".jpg") or url.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"


def build_evaluation_data(
    model_id: str, 
    prompt: str, 
    userMessageId: str, 
    modelAMessageId: str, 
    evaluationSessionId: str, 
    media: Optional[MediaListType] = None, 
    source_messages: Optional[Messages] = None, 
    conversation: Optional[JsonConversation] = None, 
    is_image_model: bool = False
) -> Dict[str, Any]:
    """
    Build the evaluation data payload for LMArena API requests.
    
    Args:
        model_id: The ID of the model to use
        prompt: The user's prompt message
        userMessageId: Unique ID for the user message
        modelAMessageId: Unique ID for the model message
        evaluationSessionId: Unique ID for the evaluation session
        media: Media attachments (optional)
        messages: Messages list (optional)
        conversation: Conversation object (optional)
        is_image_model: Whether this is an image model (default: False)
        
    Returns:
        dict: The data payload for the API request
    """
    # Process media attachments if provided
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

    # use_conversation_file = False
    # EVALUATION_SESSION_ID = evaluationSessionId

    # if hasattr(conversation,"id") :
    #     use_conversation_file=True
    #     conversation_json = ConversationJson(conversation.id)
    #     conversation_json.load()
    #     EVALUATION_SESSION_ID = conversation.id
    # else:
    # use_conversation_file=True
    # conversation_json = ConversationJson(evaluationSessionId)
    # conversation_json.load()
    EVALUATION_SESSION_ID = evaluationSessionId

    # messageHistory = conversation_json.get("messageHistory")
    #_lastEvaluationSessionId = conversation_json.get("evaluationSessionId")

  
    # conversation_json.set("evaluationSessionId",EVALUATION_SESSION_ID)
    # _evaluationSessionId,_model_id,_userMessageId,_modelAMessageId = conversation_json.get_or_set_default_config(evaluationSessionId,model_id,userMessageId,modelAMessageId)
    # INITAL FIRST MESSAGE
    processed_messages=[]
    system_messages=[]
    for message in source_messages:
        if message["role"] == "system":
            system_messages.append(message)
        else:
            processed_messages.append(message)
    final_source_messages=[]
    if len(system_messages):
        system_messages_contents =[]
        for message in system_messages:
            if isinstance(message["content"],List):
                sub_contents=[]
                for block in message["content"]:
                    if "type" in block:
                        if block["type"] == "text":
                            sub_contents.append(block["text"])
                system_messages_contents.append("\n".join(sub_contents))
            else:
                system_messages_contents.append(message["content"])

    if len(system_messages)>0:
        final_source_messages.append({
            "role":"system",
            "content":"\n".join(system_messages_contents)
        })

    for message in processed_messages:
        if isinstance(message["content"],List):
            contents=[]
            for block in message["content"]:
                if "type" in block:
                    if block["type"] == "text":
                        contents.append(block["text"])
            final_source_messages.append({
                "role":message["role"],
                "content":"\n".join(contents)
            })
        else:
            final_source_messages.append({
                "role":message["role"],
                "content":message["content"]
            })

    # try to build valid message
    final_messages=[]
    final_source_messages_len = len(final_source_messages)
    final_source_messages_index =0
    system_message_id = str(uuid.uuid4())
    # user_message_id = str(uuid.uuid4())
    last_user_message_id = None
    last_assistant_message_id = None
    for message in final_source_messages:
        is_last_index = final_source_messages_index == final_source_messages_len - 1
        if message["role"] == "system":
            final_messages.append({
                "id": system_message_id,
                "role": "system",
                "content": message["content"],
                "experimental_attachments": experimental_attachments,
                "parentMessageIds": [],
                "participantPosition": "a",
                "modelId": None,
                "evaluationSessionId": EVALUATION_SESSION_ID,
                "status": "pending",
                "failureReason": None
            })
            pass
        elif message["role"]=="user":
            user_message_id = str(uuid.uuid4())
            future_assistant_message_id = str(uuid.uuid4())
            parentMessageIds=[]
            if last_assistant_message_id:
                parentMessageIds=[last_assistant_message_id]
            if is_last_index:
                userMessageId = user_message_id
                modelAMessageId = future_assistant_message_id
                final_messages.append({
                    "id": user_message_id,
                    "role": "user",
                    "content": message["content"],
                    "experimental_attachments": experimental_attachments,
                    "parentMessageIds": parentMessageIds,
                    "participantPosition": "a",
                    "modelId": None,
                    "evaluationSessionId": EVALUATION_SESSION_ID,
                    "status": "pending",
                    "failureReason": None
                })
                final_messages.append({
                    "id": future_assistant_message_id,
                    "role": "assistant",
                    "content": "",
                    "experimental_attachments": [],
                    "parentMessageIds": [user_message_id],
                    "participantPosition": "a",
                    "modelId": model_id,
                    "evaluationSessionId": EVALUATION_SESSION_ID,
                    "status": "pending",
                    "failureReason": None
                })
            else:
                final_messages.append({
                    "id": user_message_id,
                    "role": "user",
                    "content":  message["content"],
                    "experimental_attachments": experimental_attachments,
                    "parentMessageIds": parentMessageIds,
                    "participantPosition": "a",
                    "modelId": None,
                    "evaluationSessionId": EVALUATION_SESSION_ID,
                    "status": "success",
                    "failureReason": None
                })
            pass
            last_user_message_id = user_message_id
            
        elif message["role"]=="assistant":
            assistant_message_id = str(uuid.uuid4())
            final_messages.append({
                "id": assistant_message_id,
                "role": "assistant",
                "content": message["content"],
                "experimental_attachments": experimental_attachments,
                "parentMessageIds": [last_user_message_id],
                "participantPosition": "a",
                "modelId": None,
                "evaluationSessionId": EVALUATION_SESSION_ID,
                "status": "success",
                "failureReason": None
            })
            last_assistant_message_id=assistant_message_id
            
        final_source_messages_index += 1

    messages = final_messages
    
    
    data = {
        "id": EVALUATION_SESSION_ID,
        "mode": "direct",
        "modelAId": model_id,
        "userMessageId": userMessageId,
        "modelAMessageId": modelAMessageId,
        "messages": messages,
        "modality": "image" if is_image_model else "chat"
    }
    # print(data)
    # exit()
    LOG_MESSAGE_TO_FILE=False
    if LOG_MESSAGE_TO_FILE:
        try:
            # Transform messages sebelum diproses atau disimpan
            
            # Tambahkan rutin untuk menyimpan messages ke file JSON
            log_dir = "examples/logs/request_messages/LMArenaBeta"
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
                json.dump(data, log_file, default=custom_json_serializer, ensure_ascii=False, indent=2)
        except Exception as e:
            debug.log(f"Error saving messages log: {e}")
    return data