# OpenAI Chat API

A REST API that provides access to OpenAI GPT models using your own OpenAI API key.

## Features

- Multiple OpenAI GPT models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini
- Regular chat completions with conversation history
- Streaming responses for real-time output
- Token usage tracking
- CORS enabled for cross-origin requests

## API Endpoints

### API Information
```bash
GET /
```

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "OpenAI Chat API",
  "version": "1.0.0",
  "description": "REST API for OpenAI GPT models",
  "endpoints": {
    "GET /health": "Check API health status",
    "GET /models": "List available models",
    "POST /chat": "Create chat completion",
    "POST /chat/stream": "Create streaming chat completion"
  },
  "documentation": "See README.md for usage examples"
}
```

### Health Check
```bash
GET /health
```

Returns the API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "OpenAI Chat API",
  "provider": "OpenAI"
}
```

### List Available Models
```bash
GET /models
```

Returns all available GPT models.

**Response:**
```json
{
  "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
  "default": "gpt-4o-mini"
}
```

### Chat Completion
```bash
POST /chat
```

Send a message and get a response from the AI.

**Request Body:**
```json
{
  "message": "Your message here",
  "model": "gpt-4o-mini",
  "messages": []
}
```

**Parameters:**
- `message` (required): The user's message
- `model` (optional): Model to use (default: "gpt-4o-mini")
- `messages` (optional): Conversation history array

**Response:**
```json
{
  "response": "AI response here",
  "model": "gpt-4o-mini",
  "conversation": [
    {"role": "user", "content": "Your message"},
    {"role": "assistant", "content": "AI response"}
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 10,
    "total_tokens": 22
  }
}
```

### Streaming Chat
```bash
POST /chat/stream
```

Get streaming responses in real-time (Server-Sent Events).

**Request Body:**
```json
{
  "message": "Your message here",
  "model": "gpt-4o-mini",
  "messages": []
}
```

**Response:** Server-Sent Events stream
```
data: {"content": "Hello"}
data: {"content": " there"}
data: {"done": true}
```

## Usage Examples

### Basic Chat
```bash
curl -X POST http://your-repl-url/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "model": "gpt-4o-mini"
  }'
```

### With Conversation History
```bash
curl -X POST http://your-repl-url/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "And what about Spain?",
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"},
      {"role": "assistant", "content": "The capital of France is Paris."}
    ]
  }'
```

### Streaming Response
```bash
curl -X POST http://your-repl-url/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a short poem",
    "model": "gpt-4o-mini"
  }'
```

## Available Models

- `gpt-4o` - Most capable GPT-4 model, great for complex tasks
- `gpt-4o-mini` - Fast and affordable, recommended for most uses (default)
- `gpt-4-turbo` - High-performance GPT-4 variant
- `gpt-4` - Standard GPT-4 model
- `gpt-3.5-turbo` - Fast and cost-effective
- `o1-preview` - Advanced reasoning model for complex problems
- `o1-mini` - Faster reasoning model

## Error Handling

All endpoints return proper HTTP status codes:
- `200`: Success
- `400`: Bad request (missing required fields)
- `500`: Server error

Error responses include a descriptive message:
```json
{
  "error": "Error description here"
}
```

## Running Locally

The API runs on port 5000:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 main:app
```

## Configuration

The API requires the `OPENAI_API_KEY_CYB_SEC` environment variable to be set with your OpenAI API key.

## Notes

- Uses your own OpenAI API key for secure access
- CORS is enabled for all origins
- Production-ready with Gunicorn WSGI server
