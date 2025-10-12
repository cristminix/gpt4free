# Factory AI Transparent Proxy

A FastAPI-based transparent proxy for Factory AI's API endpoints.

## Features

- **Three API Endpoints**: Supports GPT, Anthropic, and GLM models
- **Streaming Support**: Handles both streaming and non-streaming responses
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

- **GET** `/health` - Health check endpoint

### GPT Endpoint

- **POST** `/gpt` - Forwards to Factory AI's GPT endpoint

Request body:

```json
{
  "model": "gpt-5-2025-08-07",
  "input": [{ "role": "user", "content": "Hello!" }],
  "stream": true,
  "instructions": "Optional system prompt"
}
```

### Anthropic Endpoint

- **POST** `/anthropic` - Forwards to Factory AI's Anthropic endpoint

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

### GLM Endpoint

- **POST** `/glm` - Forwards to Factory AI's GLM endpoint

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

## Error Handling

The proxy returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid JSON in request body
- `502`: Request failed (upstream error)
- `504`: Request timeout

## Development

To run in development mode with auto-reload:

```bash
uv run uvicorn examples.factory_transparent_proxy.create_transparent_proxy:app --host 0.0.0.0 --port 7777 --reload
```

## License

This proxy is part of the gpt4free project.
