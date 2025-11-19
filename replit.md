# OpenAI Chat API

## Overview

This is a REST API service that provides a secure interface to OpenAI GPT models using the user's own OpenAI API key stored in environment variables.

The API exposes endpoints for health checking, listing available models, and creating chat completions with support for both standard and streaming responses.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Technology**: Flask (Python web framework)
- **Rationale**: Lightweight and straightforward for building REST APIs with minimal overhead
- **Key Features**:
  - Simple routing system for HTTP endpoints
  - Built-in JSON response handling
  - Easy integration with OpenAI Python SDK

### Cross-Origin Resource Sharing (CORS)
- **Implementation**: Flask-CORS extension
- **Configuration**: Enabled globally for all routes
- **Rationale**: Allows the API to be consumed by frontend applications hosted on different domains, making it suitable for web-based chat interfaces

### API Client Architecture
- **Client Library**: OpenAI Python SDK
- **Configuration Method**: Environment variable-based configuration
  - API key injected via `OPENAI_API_KEY_CYB_SEC`
- **Rationale**: Uses direct OpenAI API access with user's own API key for secure, production-ready deployment

### Model Support
- **Available Models**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini
- **Default Model**: gpt-4o-mini
- **Design Pattern**: Hardcoded model list with validation
- **Rationale**: Provides controlled access to specific OpenAI models via direct API integration

### API Endpoints
1. **Health Check** (`GET /health`)
   - Purpose: Service monitoring and availability verification
   - Returns service status and integration type

2. **Model Listing** (`GET /models`)
   - Purpose: Discover available models programmatically
   - Returns array of model names and default model identifier

3. **Chat Completion** (`POST /chat`)
   - Purpose: Process chat messages and return AI-generated responses
   - Supports conversation history and message formatting
   - Returns complete response with token usage statistics

4. **Streaming Chat** (`POST /chat/stream`)
   - Purpose: Real-time streaming responses using Server-Sent Events
   - Streams token-by-token for improved user experience
   - Handles conversation history and message formatting

### Response Handling
- **Standard Responses**: JSON-formatted data using Flask's `jsonify()`
- **Streaming Support**: Uses `stream_with_context` for real-time streaming responses
- **Rationale**: Streaming allows for better user experience with long responses, showing partial results as they're generated

### Error Handling
- **Validation**: Request body validation for required fields (e.g., 'message' field)
- **HTTP Status Codes**: Standard REST API status codes for success and error conditions

## External Dependencies

### Third-Party Services
- **OpenAI API** (Direct access)
  - Purpose: Access to GPT language models
  - Authentication: User's own OpenAI API key via environment variables
  - Billing: Charged directly to user's OpenAI account

### Python Packages
- **Flask**: Web framework for API server
- **flask-cors**: CORS handling middleware
- **openai**: Official OpenAI Python client library

### Environment Configuration
- **Required Environment Variables**:
  - `OPENAI_API_KEY_CYB_SEC`: User's OpenAI API key for authentication

### Infrastructure
- **Hosting Platform**: Replit
- **Runtime**: Python 3.11
- **Web Server**: Gunicorn (production WSGI server)
- **Workers**: 2 workers with 120-second timeout
- **API Access**: Direct connection to OpenAI API