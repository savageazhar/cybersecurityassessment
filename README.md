# OpenAI Chat API

A REST API that provides access to OpenAI GPT models through Replit AI Integrations. No API key required - usage is billed to your Replit credits.

## Features

- Multiple OpenAI GPT models (GPT-4o, GPT-4.1, GPT-5, and more)
- Regular chat completions with conversation history
- Streaming responses for real-time output
- Token usage tracking
- CORS enabled for cross-origin requests

## API Endpoints

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
  "integration": "Replit AI Integrations"
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
  "models": ["gpt-5", "gpt-5-mini", "gpt-4.1", "gpt-4o", ...],
  "default": "gpt-4o"
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
- `model` (optional): Model to use (default: "gpt-4o")
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

- `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
- `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- `gpt-4o`, `gpt-4o-mini`
- `o4-mini`, `o3`, `o3-mini`

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
python main.py
```

## Notes

- This API uses Replit AI Integrations
- No personal API key required
- Usage is billed to your Replit credits
- CORS is enabled for all origins
