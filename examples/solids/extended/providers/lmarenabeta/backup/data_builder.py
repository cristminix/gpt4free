"""
Data builder utilities for LMArena Beta provider.
"""
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Any
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
    messages: Optional[Messages] = None, 
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

    use_conversation_file = False
    EVALUATION_SESSION_ID = evaluationSessionId

    if hasattr(conversation,"id") :
        use_conversation_file=True
        conversation_json = ConversationJson(conversation.id)
        conversation_json.load()
        EVALUATION_SESSION_ID = conversation.id
   
    messageHistory = conversation_json.get("messageHistory")
    #_lastEvaluationSessionId = conversation_json.get("evaluationSessionId")

  
    conversation_json.set("evaluationSessionId",EVALUATION_SESSION_ID)
    if not messageHistory:
        _evaluationSessionId,_model_id,_userMessageId,_modelAMessageId = conversation_json.get_or_set_default_config(evaluationSessionId,model_id,userMessageId,modelAMessageId)
        # INITAL FIRST MESSAGE
        messages = [
                {
                    "id": userMessageId,
                    "role": "user",
                    "content": prompt,
                    "experimental_attachments": experimental_attachments,
                    "parentMessageIds": parentMessageIds,
                    "participantPosition": "a",
                    "modelId": None,
                    "evaluationSessionId": EVALUATION_SESSION_ID,
                    "status": "pending",
                    "failureReason": None
                },
                {
                    "id": _modelAMessageId,
                    "role": "assistant",
                    "content": "",
                    "experimental_attachments": [],
                    "parentMessageIds": [userMessageId],
                    "participantPosition": "a",
                    "modelId": model_id,
                    "evaluationSessionId": EVALUATION_SESSION_ID,
                    "status": "pending",
                    "failureReason": None
                }
            ]
    else:
        messages = messageHistory
        _lastModelAMessageId = conversation_json.get("modelAMessageId")
        parentMessageIds= [_lastModelAMessageId]
        conversation_json.set("modelAMessageId",modelAMessageId)
        messages.append({
                "id": userMessageId,
                "role": "user",
                "content": prompt,
                "experimental_attachments": experimental_attachments,
                "parentMessageIds": parentMessageIds,
                "participantPosition": "a",
                "modelId": None,
                "evaluationSessionId": EVALUATION_SESSION_ID,
                "status": "pending",
                "failureReason": None
            })

        messages.append({
                "id": modelAMessageId,
                "role": "assistant",
                "content": "",
                "experimental_attachments": [],
                "parentMessageIds": [userMessageId],
                "participantPosition": "a",
                "modelId": model_id,
                "evaluationSessionId": EVALUATION_SESSION_ID,
                "status": "pending",
                "failureReason": None
            })
    if use_conversation_file:
        conversation_json.set("lastMessage",messages)    
       
    if hasattr(conversation,"message_ids") :
        parentMessageIds = conversation.message_ids
    data = {
        "id": EVALUATION_SESSION_ID,
        "mode": "direct",
        "modelAId": model_id,
        "userMessageId": userMessageId,
        "modelAMessageId": modelAMessageId,
        "messages": messages,
        "modality": "image" if is_image_model else "chat"
    }
    # exit()
    LOG_MESSAGE_TO_FILE=True
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