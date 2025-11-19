# OpenAI Chat API

## Overview

This is a REST API service that provides a proxy interface to OpenAI GPT models through Replit AI Integrations. The service eliminates the need for users to manage their own OpenAI API keys by leveraging Replit's AI integration infrastructure, where usage is billed directly to Replit credits.

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
  - API key injected via `AI_INTEGRATIONS_OPENAI_API_KEY`
  - Custom base URL via `AI_INTEGRATIONS_OPENAI_BASE_URL`
- **Rationale**: Uses Replit's AI integration proxy instead of direct OpenAI API access, enabling billing through Replit credits rather than requiring user API keys

### Model Support
- **Available Models**: Multiple GPT variants including GPT-5, GPT-4.1, GPT-4o series, and o-series models
- **Default Model**: gpt-4o
- **Design Pattern**: Hardcoded model list with validation
- **Rationale**: Provides controlled access to specific models supported by Replit's AI integration layer

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
- **OpenAI API** (via Replit AI Integrations proxy)
  - Purpose: Access to GPT language models
  - Authentication: Managed through Replit environment variables
  - Billing: Charged to Replit credits instead of direct OpenAI billing

### Python Packages
- **Flask**: Web framework for API server
- **flask-cors**: CORS handling middleware
- **openai**: Official OpenAI Python client library

### Environment Configuration
- **Required Environment Variables**:
  - `AI_INTEGRATIONS_OPENAI_API_KEY`: Authentication token for Replit AI integration
  - `AI_INTEGRATIONS_OPENAI_BASE_URL`: Custom endpoint URL for Replit's OpenAI proxy

### Infrastructure
- **Hosting Platform**: Replit
- **Runtime**: Python (version not specified in repository)
- **Integration Layer**: Replit AI Integrations service acts as intermediary between application and OpenAI