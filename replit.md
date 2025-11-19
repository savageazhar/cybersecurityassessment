# AI Chat - Intelligent Conversation Platform

## Overview

A modern AI chat application with user authentication, OpenAI GPT integration, and a stunning futuristic design. The platform provides seamless access to multiple AI models for intelligent conversations and assistance.

The application features:
- **Landing Page**: Modern AI-focused website with dark theme, neon green accents, and animated tech particles
- **User Authentication**: Secure signup/login system with PostgreSQL database storage
- **AI Chat Interface**: OpenAI GPT integration for intelligent assistance (protected by authentication)
- **REST API**: Programmatic access for chat completions and streaming
- **Multi-Model Support**: Choose from 6 different OpenAI models (GPT-4o, GPT-4.1 series, GPT-3.5)
- **Streaming Responses**: Real-time AI responses with word-by-word display
- **Token Usage Tracking**: Monitor API usage and costs
- **CORS Enabled**: Ready for cross-origin requests from web applications

## User Preferences

Preferred communication style: Simple, everyday language.

## Contact Information

- **Phone**: +91 83406 00849
- **Email**: mdazruddin.dilansari@gmail.com

## System Architecture

### Backend Framework
- **Technology**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with session-based auth
- **Security**: CSRF protection with Flask-WTF, password hashing with Werkzeug
- **Key Features**:
  - RESTful API endpoints
  - Session management
  - Database models for user management
  - OpenAI SDK integration

### Frontend Architecture
- **Design Theme**: Dark futuristic AI-focused style
  - Dark background (#0a0e1a)
  - Neon green accents (#00ff88)
  - Glassmorphism effects with backdrop blur
  - Animated particle backgrounds with tech symbols
  - GSAP-powered scroll animations
- **Technology Stack**:
  - HTML5, CSS3, Vanilla JavaScript
  - GSAP for animations
  - Custom particle system with canvas
  - Font Awesome icons
  - Fully responsive design

### Pages & Routes

#### Public Pages
1. **Homepage** (`GET /`)
   - Modern AI Chat landing page (prop_firm.html)
   - Hero section: "Intelligent AI Assistant — Powered by OpenAI"
   - Transparent navbar with glass effect
   - Navigation: Home, Features, Models, About, Contact
   - Actions: Language Selector, Login/Register, Start Chatting buttons
   - Sections: Features (streaming, models, history), AI Models (GPT-4o, GPT-4.1, GPT-4o Mini), Stats, About
   - Animated particle background with tech symbols (AI, GPT, ML, CODE, API, TECH, DATA, { }, </>, ∞)
   - Cookie consent banner
   - Social media icons (fixed bottom-left)
   - Play button for intro video
   - Scroll-to-explore indicator

2. **Login Page** (`GET/POST /login`)
   - AI Chat themed login interface
   - Email/phone and password authentication
   - CSRF-protected form submissions
   - Animated tech elements background (AI, GPT-4, ∞)
   - Split layout with AI features showcase
   - Link to signup page

3. **Signup Page** (`GET/POST /signup`)
   - AI Chat themed registration interface
   - Fields: name, email, phone, password
   - CSRF-protected form submissions
   - Benefits showcase section (free access, multiple models, conversation history, streaming)
   - Animated tech background (GPT, AI, 4.0)
   - Link to login page

4. **About Page** (`GET /about`)
   - Company/platform information
   - AI Chat theme

#### Protected Pages (Require Login)
5. **Chat Interface** (`GET /chat`)
   - AI-powered trading assistant
   - Model selector dropdown
   - Real-time streaming responses
   - Conversation history
   - Logout functionality
   - User information display

### Database Schema

#### Users Table
- `id`: Integer, Primary Key
- `name`: String(100), Not Null
- `email`: String(120), Unique, Not Null
- `phone`: String(20), Not Null
- `password_hash`: String(255), Not Null
- `created_at`: DateTime, Default UTC Now

### Authentication System
- **Session-Based**: Flask-Login manages user sessions
- **Password Security**: Werkzeug password hashing (bcrypt)
- **CSRF Protection**: 
  - Global CSRFProtect enabled
  - Login/signup routes use @csrf.exempt with manual validation
  - Form submissions require valid CSRF tokens
  - JSON API requests exempted from CSRF
  - Chat endpoints (@csrf.exempt) for API usage
- **Protected Routes**: @login_required decorator on chat endpoints
- **Redirect Logic**: Authenticated users redirected to chat, unauthenticated to login

### API Endpoints

#### Authentication
1. **Login** (`POST /login`)
   - Accepts: form data or JSON
   - Returns: redirect to chat (form) or JSON response
   - CSRF: validated for form submissions

2. **Signup** (`POST /signup`)
   - Accepts: form data or JSON
   - Creates new user account
   - CSRF: validated for form submissions

3. **Logout** (`GET /logout`)
   - Ends user session
   - Redirects to homepage

#### AI Chat (Protected)
4. **Chat Completion** (`POST /chat`)
   - Requires authentication
   - CSRF exempt (JSON API)
   - Returns complete AI response with token stats

5. **Streaming Chat** (`POST /chat/stream`)
   - Requires authentication
   - CSRF exempt (JSON API)
   - Server-Sent Events for real-time streaming

#### Utility
6. **API Info** (`GET /api`)
   - API documentation

7. **Health Check** (`GET /health`)
   - Service status monitoring

8. **Model Listing** (`GET /models`)
   - Available OpenAI models

### Static Assets

#### CSS
- `static/css/prop_firm.css`
  - Complete styling for landing page
  - Dark theme with CSS variables
  - Glassmorphism card effects
  - Responsive breakpoints (mobile, tablet, desktop)
  - Animations and transitions
  - Accessibility (prefers-reduced-motion)

#### JavaScript
- `static/js/prop_firm.js`
  - GSAP ScrollTrigger animations
  - Scroll effects and parallax
  - Counter animations for stats
  - Cookie consent handling
  - Video modal functionality
  - Mobile menu toggle
  - Floating element animations
  - Glassmorphism hover effects

- `static/js/particles.js`
  - Custom particle system using Canvas API
  - Floating numbers, currency symbols, trading pairs
  - Connection lines between particles
  - Pulse animations
  - Performance optimized with requestAnimationFrame

### Animation System
- **GSAP**: Professional-grade JavaScript animation library
  - ScrollTrigger for scroll-based animations
  - Smooth parallax effects
  - Card entrance animations
  - Floating button animations
  - Counter number animations
- **CSS Animations**: 
  - Glow effects on text
  - Floating elements
  - Pulse animations
  - Smooth transitions
- **Particle System**:
  - Tech symbols (AI, GPT, ML, CODE, DATA, TECH, API)
  - Programming symbols ({ }, </>, +, -, *, /, <, >, =, ∞)
  - Numbers and mathematical elements
  - Dynamic connections between particles

### Design System

#### Colors
- `--neon-green`: #00ff88 (Primary accent)
- `--dark-bg`: #0a0e1a (Background)
- `--glass-bg`: rgba(255, 255, 255, 0.05) (Cards)
- `--glass-border`: rgba(255, 255, 255, 0.1) (Borders)
- `--text-primary`: #ffffff (Main text)
- `--text-secondary`: #94a3b8 (Secondary text)

#### Components
- **Glassmorphism Cards**: backdrop-filter blur with transparent backgrounds
- **Neon Glow Text**: Gradient text with glow shadows
- **Glass Navbar**: Fixed transparent navigation with blur
- **Gradient Buttons**: Neon green gradients with hover effects
- **Floating Elements**: Animated currency/trading symbols
- **Cookie Consent**: Glass card with Accept/Decline buttons
- **Social Icons**: Fixed bottom-left with hover animations

#### Responsive Design
- **Desktop**: 1200px+ (full layout)
- **Tablet**: 768-1199px (adjusted grids)
- **Mobile**: <768px (single column, hamburger menu)

### OpenAI Integration
- **Available Models**: 6 models
  - gpt-4o, gpt-4o-mini
  - gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
  - gpt-3.5-turbo
- **Default Model**: gpt-4o-mini
- **API Key**: Environment variable `OPENAI_API_KEY_CYB_SEC`
- **Features**: 
  - Streaming responses
  - Token usage tracking
  - Conversation history
  - Error handling

### Security Features
1. **CSRF Protection**: Flask-WTF with manual validation for forms
2. **Password Hashing**: Werkzeug security functions
3. **Session Management**: Flask-Login secure sessions
4. **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
5. **Environment Variables**: Sensitive data in env vars
6. **HTTPS Ready**: Secure headers and cookie settings

### External Dependencies

#### Python Packages
- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- Flask-SQLAlchemy: Database ORM
- Flask-Login: Session management
- Flask-WTF: CSRF protection and forms
- Werkzeug: Password hashing
- OpenAI: Official Python SDK
- Gunicorn: Production WSGI server
- psycopg2-binary: PostgreSQL adapter
- email-validator: Email validation

#### Frontend Libraries (CDN)
- Font Awesome 6.4.0: Icons
- GSAP 3.12.2: Animations
- ScrollTrigger: Scroll animations

### Infrastructure
- **Hosting**: Replit
- **Runtime**: Python 3.11
- **Web Server**: Gunicorn (2 workers, 120s timeout)
- **Database**: PostgreSQL (Neon-backed)
- **Port**: 5000 (bound to 0.0.0.0)

### Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY_CYB_SEC`: OpenAI API key
- `SECRET_KEY`: Flask session secret (auto-generated in dev)

### Recent Updates (November 2025)
- Transformed website from prop-trading to AI chat focus
- Removed all crypto/trading/challenge references
- Updated particles to show tech symbols (AI, GPT, ML, CODE, etc.) instead of trading symbols
- Changed branding from PROPFIRM to AICHAT throughout
- Updated hero section to "Intelligent AI Assistant — Powered by OpenAI"
- Redesigned sections: Features (streaming, models, history), AI Models showcase, relevant stats
- Updated login/signup pages with AI chat messaging
- Maintained dark neon aesthetic (#0a0e1a background, #00ff88 accent)
- Preserved glassmorphism effects and GSAP animations
- Updated footer with contact information and AI Chat branding
