# Factory AI Transparent Proxy

A FastAPI-based transparent proxy for Factory AI's API endpoints.

## Features

- **Three API Endpoints**: Supports GPT, Anthropic, and GLM models
- **Multiple Endpoint Aliases**: Each provider has alternative endpoint paths for compatibility
- **Streaming Support**: Handles both streaming and non-streaming responses
- **Model Mapping**: Automatic model name mapping for Anthropic models
- **Message Transformation**: Intelligent message content handling (supports both string and list formats)
- **Proxy Support**: Optional HTTP proxy configuration via `SET_PROXY` environment variable
- **Browser Impersonation**: Uses Chrome impersonation for requests
- **Easy to Use**: Simple REST API interface
- **Environment-based Auth**: Uses `.env` file for API key management

## Prerequisites

1. Python 3.8+
2. Factory AI API token (set in `.env` file)

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your API token in `.env` file:

```bash
FACTORY_AI_TOKEN="your_token_here"
SET_PROXY="http://proxy:port"  # Optional
```

## Running the Proxy

Using `uv` (recommended):

```bash
uv run uvicorn examples.factory_transparent_proxy.create_transparent_proxy:app --host 0.0.0.0 --port 7777 --reload
```

Or using standard Python:

```bash
python -m uvicorn examples.factory_transparent_proxy.create_transparent_proxy:app --host 0.0.0.0 --port 7777 --reload
```

The proxy will be available at `http://localhost:7777`

## API Endpoints

### Root Endpoint

- **GET** `/` - API information and status

### Health Check

- **GET** `/health` - Health check endpoint (returns status and API key configuration)

### GPT Endpoints

- **POST** `/gpt` - Forwards to Factory AI's GPT endpoint
- **POST** `/responses` - Alias for `/gpt` endpoint

Request body:

```json
{
  "model": "gpt-5-2025-08-07",
  "input": [{ "role": "user", "content": "Hello!" }],
  "stream": true,
  "instructions": "Optional system prompt"
}
```

### Anthropic Endpoints

- **POST** `/anthropic` - Forwards to Factory AI's Anthropic endpoint
- **POST** `/v1/messages` - Alias for `/anthropic` endpoint (OpenAI-compatible path)

Request body:

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "messages": [{ "role": "user", "content": "Hello!" }],
  "stream": true,
  "max_tokens": 32000,
  "temperature": 1,
  "system": "Optional system prompt"
}
```

**Supported Model Aliases:**

- `claude-opus-4` → `claude-opus-4-1-20250805`
- `claude-sonnet-4.5` or `claude-sonnet-4-5` → `claude-sonnet-4-5-20250929`
- `claude-sonnet-4` → `claude-sonnet-4-20250514`

### GLM Endpoints

- **POST** `/glm` - Forwards to Factory AI's GLM endpoint
- **POST** `/v1/chat/completions` - Alias for `/glm` endpoint (OpenAI-compatible path)

Request body:

```json
{
  "model": "glm-4.6",
  "messages": [{ "role": "user", "content": "Hello!" }],
  "stream": true,
  "max_tokens": 32000,
  "temperature": 1
}
```

## Example Usage

### Using cURL

Non-streaming request:

```bash
curl -X POST http://localhost:7777/gpt \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5-2025-08-07",
    "input": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

Streaming request:

```bash
curl -X POST http://localhost:7777/gpt \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5-2025-08-07",
    "input": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

### Using Python

```python
import httpx
import json

# Non-streaming
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:7777/gpt",
        json={
            "model": "gpt-5-2025-08-07",
            "input": [{"role": "user", "content": "Hello!"}],
            "stream": False
        }
    )
    print(response.json())

# Streaming
async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:7777/gpt",
        json={
            "model": "gpt-5-2025-08-07",
            "input": [{"role": "user", "content": "Hello!"}],
            "stream": True
        }
    ) as response:
        async for chunk in response.aiter_bytes():
            print(chunk.decode())
```

## Architecture

The proxy acts as a transparent middleman between your application and Factory AI's API:

```
Your App → Transparent Proxy → Factory AI API
         ← Transparent Proxy ←
```

Benefits:

- Single point of configuration for API keys
- Easy monitoring and logging
- Rate limiting capabilities (can be added)
- Request/response transformation if needed

## Environment Variables

- `FACTORY_AI_TOKEN`: Your Factory AI API token (required)
- `SET_PROXY`: HTTP proxy URL (optional, e.g., `http://proxy:port`)

## Error Handling

The proxy returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid JSON in request body
- `500`: Internal server error (streaming error, JSON parsing failure)
- `502`: Request failed (upstream error)

## Technical Details

### Message Content Handling

The proxy intelligently handles message content in multiple formats:

- **String content**: Passed through directly
- **List content**: Automatically combined into a single string (extracts `text` from content parts)

### Request Transformation

Each API provider has specific request transformations:

- **GPT**: Uses `input` field for messages, adds default system prompt signature
- **Anthropic**: Filters out system messages from message array, combines them into `system` field
- **GLM**: Converts to standard chat format with system message prepended

### Provider Headers

The proxy automatically sets the correct `x-api-provider` header:

- GPT: `azure_openai`
- Anthropic: `anthropic`
- GLM: `fireworks`

### Browser Impersonation

All requests use Chrome browser impersonation via [`g4f.requests.StreamSession`](../../g4f/requests/__init__.py) for better compatibility.

## Development

To run in development mode with auto-reload:

```bash
uv run uvicorn examples.factory_transparent_proxy.create_transparent_proxy:app --host 0.0.0.0 --port 7777 --reload
```

Or run directly:

```bash
python examples/factory_transparent_proxy/create_transparent_proxy.py
```

## License

This proxy is part of the gpt4free project.
