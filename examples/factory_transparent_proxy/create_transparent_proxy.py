"""
Factory AI Transparent Proxy using FastAPI

This proxy forwards requests to Factory AI's API endpoints:
- GPT endpoint: /o/v1/responses
- Anthropic endpoint: /a/v1/messages  
- GLM endpoint: /o/v1/chat/completions

Run with: uv run uvicorn examples.factory_transparent_proxy.create_transparent_proxy:app --host 0.0.0.0 --port 7777 --reload
"""

import os
import json
from typing import AsyncIterator, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from g4f.requests import StreamSession,StreamResponse, raise_for_status
# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "https://app.factory.ai/api/llm"
GPT_ENDPOINT = "o/v1/responses"
ANTHROPIC_ENDPOINT = "a/v1/messages"
GLM_ENDPOINT = "o/v1/chat/completions"

# Get API key from environment
API_KEY = os.getenv("FACTORY_AI_TOKEN")
if not API_KEY:
    raise ValueError("FACTORY_AI_TOKEN environment variable is required")

# Create FastAPI app
app = FastAPI(
    title="Factory AI Transparent Proxy",
    description="Transparent proxy for Factory AI API endpoints",
    version="1.0.0"
)


def get_headers(api_provider: str) -> dict:
    """Build request headers based on API provider type."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    if api_provider == "gpt":
        headers["x-api-provider"] = "azure_openai"
    elif api_provider == "anthropic":
        headers["x-api-provider"] = "anthropic"
    elif api_provider == "glm":
        headers["x-api-provider"] = "fireworks"
    
    return headers


async def stream_response_content(response) -> AsyncIterator[bytes]:
    """Stream response chunks from the upstream API."""
    try:
        async for chunk in response.iter_content():
            if chunk:
                yield chunk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")


async def proxy_request(
    endpoint: str,
    api_provider: str,
    request_data: dict,
    stream: bool = False,
    proxy: Optional[str] = "http://127.0.0.1:8081"
) -> StreamingResponse | JSONResponse:
    """
    Proxy request to Factory AI API.
    
    Args:
        endpoint: API endpoint path
        api_provider: API provider type (gpt, anthropic, glm)
        request_data: Request body data
        stream: Whether to stream the response
        proxy: Optional proxy URL
    
    Returns:
        StreamingResponse for streaming requests, JSONResponse otherwise
    """
    url = f"{BASE_URL}/{endpoint}"
    print(f"url:{url}")
    print(request_data)
    headers = get_headers(api_provider)
    print(headers)
    print(f"proxy:{proxy}")
    
    try:
        # Use StreamSession for streaming, StreamResponse for non-streaming
        if stream:
            async with StreamSession(
                impersonate="chrome",
                proxy=proxy,
            ) as session:  # type: ignore
                async with session.post(
                    url,
                    json=request_data,
                    headers=headers,
                ) as response:
                    # Check for errors
                    response.raise_for_status()
                    
                    # Return streaming response
                    return StreamingResponse(
                        stream_response_content(response),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        }
                    )
        else:
            # For non-streaming, use StreamSession with StreamResponse
            async with StreamSession(
                impersonate="chrome",
                proxy=proxy,
            ) as session:  # type: ignore
                async with session.post(
                    url,
                    json=request_data,
                    headers=headers,
                ) as response:  # type: ignore
                    # Check for errors
                    response.raise_for_status()
                    
                    # Handle non-streaming responses
                    try:
                        data = await response.json()
                        return JSONResponse(content=data)
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to parse response: {str(e)}"
                        )
                    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Factory AI Transparent Proxy",
        "version": "1.0.0",
        "endpoints": {
            "gpt": f"/gpt or /response (forwards to {BASE_URL}/{GPT_ENDPOINT})",
            "anthropic": f"/anthropic or /v1/messages (forwards to {BASE_URL}/{ANTHROPIC_ENDPOINT})",
            "glm": f"/glm or /v1/chat/completions (forwards to {BASE_URL}/{GLM_ENDPOINT})",
        },
        "status": "ready"
    }


@app.post("/gpt")
async def gpt_endpoint(request: Request):
    """
    GPT endpoint proxy.
    Forwards requests to Factory AI's GPT endpoint.
    
    Expected request body:
    {
        "model": "gpt-5-2025-08-07",
        "input": [...messages],
        "stream": true/false,
        "instructions": "optional system prompt"
    }
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=GPT_ENDPOINT,
            api_provider="gpt",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")


@app.post("/response")
async def response_endpoint(request: Request):
    """
    Response endpoint (alias for GPT endpoint).
    Forwards requests to Factory AI's GPT endpoint.
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=GPT_ENDPOINT,
            api_provider="gpt",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")


@app.post("/anthropic")
async def anthropic_endpoint(request: Request):
    """
    Anthropic endpoint proxy.
    Forwards requests to Factory AI's Anthropic endpoint.
    
    Expected request body:
    {
        "model": "claude-sonnet-4-5-20250929",
        "messages": [...messages],
        "stream": true/false,
        "max_tokens": 32000,
        "temperature": 1,
        "system": "optional system prompt"
    }
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=ANTHROPIC_ENDPOINT,
            api_provider="anthropic",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@app.post("/v1/messages")
async def v1_messages_endpoint(request: Request):
    """
    V1 Messages endpoint (alias for Anthropic endpoint).
    Forwards requests to Factory AI's Anthropic endpoint.
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=ANTHROPIC_ENDPOINT,
            api_provider="anthropic",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")



@app.post("/glm")
async def glm_endpoint(request: Request):
    """
    GLM endpoint proxy.
    Forwards requests to Factory AI's GLM endpoint.
    
    Expected request body:
    {
        "model": "glm-4.6",
        "messages": [...messages],
        "stream": true/false,
        "max_tokens": 32000,
        "temperature": 1
    }
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=GLM_ENDPOINT,
            api_provider="glm",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")


@app.post("/v1/chat/completions")
async def v1_chat_completions_endpoint(request: Request):
    """
    V1 Chat Completions endpoint (alias for GLM endpoint).
    Forwards requests to Factory AI's GLM endpoint.
    """
    try:
        request_data = await request.json()
        stream = request_data.get("stream", False)
        
        return await proxy_request(
            endpoint=GLM_ENDPOINT,
            api_provider="glm",
            request_data=request_data,
            stream=stream
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(API_KEY)
    }


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777, reload=True)