# AI Gateway

A powerful, multi-provider AI gateway with a modern UI and chat history.

## Features

- **Multi-Provider AI:** Seamlessly switch between OpenAI (GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo) and Google (Gemini Pro) models.
- **Modern UI:** A clean and intuitive chat interface with a chat history sidebar.
- **Chat History:** Your conversations are saved and can be revisited at any time.
- **User Authentication:** Secure user authentication and registration.
- **Streaming Responses:** Real-time output for a smooth and responsive experience.
- **CORS Enabled:** Cross-origin requests are enabled for easy integration.

## API Endpoints

### API Information
```bash
GET /api
```

Returns API information and available endpoints.

### Health Check
```bash
GET /health
```

Returns the API status.

### List Available Models
```bash
GET /models
```

Returns all available models from OpenAI and Google.

### Chat Completion
```bash
POST /api/chat
```

Send a message and get a response from the selected AI model.

### Streaming Chat
```bash
POST /api/chat/stream
```

Get streaming responses in real-time (Server-Sent Events).

### Get Chat History
```bash
GET /api/chat/history
```

Returns the chat history for the authenticated user.

## `curl` Examples

### Login
```bash
curl -X POST -H "Content-Type: application/json" -d '{"email_or_phone": "test@example.com", "password": "password"}' http://localhost:5000/login
```

### Chat
```bash
curl -X POST -H "Content-Type: application/json" -b "cookie.txt" -d '{"message": "Hello, world!", "model": "gpt-4o"}' http://localhost:5000/api/chat
```

## Running Locally

The application runs on port 5000:
```bash
python main.py
```

## Configuration

The application requires the following environment variables to be set:

- `SECRET_KEY`: A secret key for the Flask application.
- `DATABASE_URL`: The URL for the database (e.g., `sqlite:///db.sqlite3`).
- `OPENAI_API_KEY`: Your OpenAI API key.
- `GEMINI_API_KEY`: Your Google Gemini API key.
