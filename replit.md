# OpenAI Chat Application

## Overview

This is a complete chat application with both a web interface and REST API that provides access to OpenAI GPT models using the user's own OpenAI API key stored in environment variables.

The application features:
- **Homepage**: Modern landing page with hero section, feature cards, and floating chat widget
- **Full Chat Interface**: Dedicated chat page with real-time streaming responses
- **Floating Chat Widget**: Small assistant in the corner of the homepage for quick conversations
- **REST API**: Programmatic access for integration with other applications
- **Multi-Model Support**: Choose from 6 different OpenAI models (GPT-4o, GPT-4.1 series)
- **Streaming Responses**: See AI responses appear in real-time as they're generated
- **Token Usage Tracking**: Monitor prompt and completion tokens for cost tracking
- **Conversation History**: Maintain context across multiple messages
- **CORS Enabled**: Ready for cross-origin requests from web applications

## User Preferences

Preferred communication style: Simple, everyday language.

## Contact Information

- **Phone**: +91 83406 00849
- **Email**: mdazruddin.dilansari@gmail.com

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
- **Available Models**: 6 models including GPT-4o, GPT-4.1 series, and GPT-3.5
  - GPT-4o series: gpt-4o, gpt-4o-mini
  - GPT-4.1 series: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
  - Classic: gpt-3.5-turbo
- **Default Model**: gpt-4o-mini (fast and affordable)
- **Design Pattern**: Hardcoded model list with validation
- **Rationale**: Provides controlled access to specific OpenAI models via direct API integration
- **Model Selection**: Only includes models available with user's API tier (GPT-5 models require higher quota)

### Frontend Architecture
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Modern teal-blue gradient theme with mobile-responsive layout
- **Pages**:
  - **Homepage** (`/`): Landing page with hero section, feature cards, floating chat widget, and contact footer
  - **Full Chat** (`/chat`): Dedicated chat interface with model selector
- **Chat Widget Features**:
  - Floating button in bottom-right corner
  - Popup chat interface with full streaming support
  - Independent conversation history
  - Buffered SSE parsing for reliable message delivery
- **Full Chat Features**:
  - Real-time streaming chat with word-by-word response display
  - Model selector dropdown for choosing between 6 GPT models
  - Conversation history with user/assistant message bubbles
  - Typing indicators and smooth animations

### Navigation
- **Home**: Landing page with hero section and features
- **Chat**: Full-screen chat interface
- **Service**: Placeholder for future features
- **Contacts**: Scrolls to contact footer with phone and email information

### API Endpoints
1. **Homepage** (`GET /`)
   - Purpose: Serve the landing page with hero section, features, chat widget, and contact footer
   - Returns: HTML page with hero section, features, floating chat assistant, and contact information

2. **Full Chat** (`GET /chat`)
   - Purpose: Serve the dedicated full-screen chat interface
   - Returns: HTML page with full chat interface and model selector

3. **API Info** (`GET /api`)
   - Purpose: API documentation and endpoint listing
   - Returns: JSON with API metadata and available endpoints

4. **Health Check** (`GET /health`)
   - Purpose: Service monitoring and availability verification
   - Returns service status and integration type

5. **Model Listing** (`GET /models`)
   - Purpose: Discover available models programmatically
   - Returns array of model names and default model identifier

6. **Chat Completion** (`POST /chat`)
   - Purpose: Process chat messages and return AI-generated responses
   - Supports conversation history and message formatting
   - Returns complete response with token usage statistics

7. **Streaming Chat** (`POST /chat/stream`)
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