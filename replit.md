# Kimi AI - Futuristic AI Conversation Platform

## Overview

Kimi AI is a cutting-edge AI chat application designed for intelligent conversations and assistance, featuring user authentication, OpenAI GPT integration, and a futuristic dark-neon interface. It provides seamless access to multiple AI models with real-time streaming responses, professional voice features (STT and TTS), and a robust REST API. The project aims to offer a visually stunning and highly functional AI interaction platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Technology**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM for user management.
- **Authentication**: Flask-Login for session-based authentication, Flask-WTF for CSRF protection, and Werkzeug for password hashing.
- **API**: RESTful API endpoints for chat completions, streaming, and voice features.

### Frontend Architecture
- **Design Theme**: Futuristic dark AI-focused style with a dark background (`#0a0e1a`), neon green accents (`#00ff88`), glassmorphism effects, and animated particle backgrounds.
- **Technology Stack**: HTML5, CSS3, Vanilla JavaScript, GSAP for animations, Custom Canvas particle system, Font Awesome for icons, and fully responsive design.
- **Key Features**:
    - **Chat Interface**: Real-time streaming responses with typing animation, Markdown rendering (Marked.js), syntax highlighting (Highlight.js), copy buttons for code, token usage tracking, message counter, and clear chat functionality.
    - **Voice Features**: Speech-to-text (OpenAI Whisper), Text-to-speech (OpenAI TTS with 6 voice options and speed control), real-time voice visualizer, auto-play toggle, and manual playback buttons.
    - **Pages**:
        - **Public**: Homepage, Login, Signup, About pages, all themed with Kimi AI branding and animations.
        - **Protected**: Main Chat Interface with model selection, conversation history, and live statistics.

### Design System
- **Colors**: Primarily `--neon-green` (#00ff88) and `--dark-bg` (#0a0e1a), with `--glass-bg` for transparent elements.
- **Components**: Glassmorphism cards, neon glow text, glass navbar, gradient buttons, and floating animated elements.
- **Animations**: GSAP for scroll animations, parallax effects, and element transitions; CSS animations for glow and pulse effects; custom Canvas-based particle system displaying tech symbols.

### Security Features
- CSRF Protection (Flask-WTF), password hashing (Werkzeug), secure session management (Flask-Login), SQL injection prevention (SQLAlchemy), and environment variable usage for sensitive data.

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Flask-WTF**: CSRF protection and forms
- **Werkzeug**: Password hashing
- **OpenAI**: Official Python SDK for AI model integration
- **psycopg2-binary**: PostgreSQL adapter
- **email-validator**: Email validation

### Frontend Libraries (CDN)
- **Font Awesome 6.4.0**: Icons
- **GSAP 3.12.2** & **ScrollTrigger**: Advanced animations
- **Marked.js 11.0.0**: Markdown rendering
- **Highlight.js 11.9.0**: Code syntax highlighting