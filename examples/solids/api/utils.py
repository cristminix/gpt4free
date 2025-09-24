"""
Utility functions for the API module
"""
import base64
import json
import os
import tempfile
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from urllib.parse import urlparse

from g4f import debug
from g4f.typing import Messages, Message, ContentPart


def write_file_from_base64_url(data_url: str) -> Optional[str]:
    """
    Write a file from a base64 data URL and return the file path.
    
    Args:
        data_url (str): Base64 data URL (e.g., data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...)
        
    Returns:
        Optional[str]: Path to the created file, or None if failed
    """
    try:
        # Parse the data URL
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format")
            
        # Extract the media type and base64 data
        header, base64_data = data_url.split(",", 1)
        media_type = header.split(";")[0].split(":")[1] if ";" in header else header.split(":")[1]
        
        # Decode base64 data
        file_data = base64.b64decode(base64_data)
        
        # Determine file extension based on media type
        extension_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }
        extension = extension_map.get(media_type, ".bin")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(file_data)
            return temp_file.name
            
    except Exception as e:
        print(f"Error writing file from base64 URL: {e}")
        return None
async def get_messages(input_messages: Messages, provider_api: Any=None) -> Messages:
    """
    Process chat messages, combining system messages if there are more than one,
    and handling user content that may contain text and images.
    
    Args:
        input_messages (Messages): List of input messages
        provider_api (Any): Provider API object with uploadFile method
        
    Returns:
        Messages: Processed list of messages
    """
    # Filter and combine system messages if there are more than one
    system_messages = [msg for msg in input_messages if msg["role"] == "system"]
    processed_messages = input_messages
    
    if len(system_messages) > 1:
        combined_system_content = []
        for msg in system_messages:
            if isinstance(msg["content"], str):
                combined_system_content.append(msg["content"])
            elif isinstance(msg["content"], list):
                system_msg_content = []
                for item in msg["content"]:
                    if item["type"] == "text":
                        system_msg_content.append(item["text"])
                if system_msg_content:
                    combined_system_content.append("\n".join(system_msg_content))
        
        # Filter out empty content
        combined_system_content = [content for content in combined_system_content if content]
        
        # Remove system messages that have been combined
        processed_messages = [msg for msg in input_messages if msg["role"] != "system"]
        
        # Add the combined system message
        if combined_system_content:
            processed_messages.insert(0, {
                "role": "system",
                "content": "\n".join(combined_system_content)
            })
    
    messages: Messages = []
    prev_msg=None
    system_message_added = False
    for msg in processed_messages:
        if msg["role"] == "user" and isinstance(msg["content"], list):
            contents: Message = {
                "role": "user",
                "content": []
            }
            for item in msg["content"]:
                if item["type"] == "image_url":
                    try:
                        image_path = write_file_from_base64_url(item["image_url"]["url"])
                        if image_path:
                            print(image_path)
                            #file_response = await provider_api.upload_file(image_path)
                            image_block: ContentPart = {
                                "type": "image_url",
                                "image_url": {
                                    #"url": file_response["file_url"]
                                }
                            }
                            contents["content"].append(image_block)  # type: ignore
                    except Exception as error:
                        print(f"Error processing image: {error}")
                else:
                    if item["type"] == "text":
                        text_block: ContentPart = {
                            "type": "text",
                            "text": item["text"]
                        }
                        contents["content"].append(text_block)  # type: ignore
            messages.append(contents)
        else:
            if msg["role"] == "system":
                # Only add system message if it hasn't been added yet
                if not system_message_added:
                    system_content_str = ""
                    system_msg_content = []
                    if isinstance(msg["content"], list):
                        for item in msg["content"]:
                            if item["type"] == "text":
                                system_msg_content.append(item["text"])
                        if system_msg_content:
                            system_content_str = "\n".join(system_msg_content)
                    else:
                        system_content_str = msg["content"] or ""
                    
                    messages.append({
                        "role": msg["role"],
                        "content": system_content_str
                    })
                    system_message_added = True
            elif msg["role"] == "tool":
                if prev_msg and "tool_calls" in prev_msg and prev_msg['tool_calls']:
                    id=prev_msg['tool_calls'][0]["id"]
                    msg["role"]="user"
                    msg["tool_call_id"]=id
                    msg["content"]=f"Tool response for call ID {id}: {msg['content']}"
                messages.append(msg)

            else:
                if not "content" in msg:
                    msg["content"]=""
                messages.append(msg)
        if "tool_calls" in msg:
            tidx=0
            for tc in msg["tool_calls"]:
                if not "type" in tc:
                    tc["type"] = "function"
                    msg["tool_calls"][tidx] = tc
                tidx += 1

        prev_msg=msg
        debug.log(msg)

    # write messages to  json to  examples/logs/request_messages/current timestamp+"message.json"
    # Get current timestamp
    current_time = datetime.now()
    timestamp_str = current_time.strftime("%Y%m%d_%H%M%S_%f")
    
    # Create filename
    filename = f"messages_{timestamp_str}.json"
    filepath = os.path.join("examples", "logs", "request_messages", filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write messages to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    return messages