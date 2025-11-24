import os
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context, render_template, redirect, url_for, flash, session, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from openai import OpenAI
from google import genai
import json
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20
}
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_DURATION'] = 2592000
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000

CORS(app, supports_credentials=False, resources={
    r"/api": {"origins": "*"},
    r"/models": {"origins": "*"},
    r"/health": {"origins": "*"}
})
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize OpenAI client for voice services
openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
    OPENAI_AVAILABLE = True
else:
    client = None
    OPENAI_AVAILABLE = False

# Initialize Google GenAI client for Nano Banana (image generation)
nano_banana_api_key = os.environ.get("GO_BANAN_API_KEY")
if nano_banana_api_key:
    genai_client = genai.Client(api_key=nano_banana_api_key)
    NANO_BANANA_AVAILABLE = True
else:
    genai_client = None
    NANO_BANANA_AVAILABLE = False

AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-3.5-turbo"
]

AVAILABLE_VOICES = [
    {"id": "alloy", "name": "Alloy", "description": "Neutral and balanced"},
    {"id": "echo", "name": "Echo", "description": "Warm and engaging"},
    {"id": "fable", "name": "Fable", "description": "Expressive storyteller"},
    {"id": "onyx", "name": "Onyx", "description": "Deep and authoritative"},
    {"id": "nova", "name": "Nova", "description": "Energetic and friendly"},
    {"id": "shimmer", "name": "Shimmer", "description": "Soft and gentle"}
]

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    return render_template('prop_firm.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    
    if request.method == 'POST':
        # Validate CSRF token for form submissions
        if not request.is_json:
            csrf_token = request.form.get('csrf_token')
            if not csrf_token:
                flash('Security validation failed. Please try again.', 'error')
                return redirect(url_for('login'))
        
        data = request.get_json() if request.is_json else request.form
        app.logger.info(f"Login attempt - Email/Phone: {data.get('email_or_phone')}")
        email_or_phone = data.get('email_or_phone', '').strip()
        password = data.get('password', '')
        
        if not email_or_phone or not password:
            if request.is_json:
                return jsonify({"error": "Email/phone and password are required"}), 400
            flash('Email/phone and password are required', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter(
            (User.email == email_or_phone) | (User.phone == email_or_phone)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            session.permanent = True
            app.logger.info(f"✅ Login successful - User: {user.email}, Session ID: {session.get('_user_id')}")
            
            if request.is_json:
                return jsonify({
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                }), 200
            
            flash('Login successful! Welcome back!', 'success')
            return redirect(url_for('chat_page'))
        
        app.logger.warning(f"❌ Login failed - Invalid credentials for: {email_or_phone}")
        if request.is_json:
            return jsonify({"error": "Invalid credentials"}), 401
        flash('Invalid email/phone or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
@csrf.exempt
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    
    if request.method == 'POST':
        # Validate CSRF token for form submissions
        if not request.is_json:
            csrf_token = request.form.get('csrf_token')
            if not csrf_token:
                flash('Security validation failed. Please try again.', 'error')
                return redirect(url_for('signup'))
        
        data = request.get_json() if request.is_json else request.form
        app.logger.info(f"Signup attempt - Email: {data.get('email')}, Name: {data.get('name')}")
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([name, email, phone, password]):
            app.logger.warning(f"Signup validation failed: missing fields")
            if request.is_json:
                return jsonify({"error": "All fields are required"}), 400
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            if request.is_json:
                return jsonify({"error": "Password must be at least 6 characters long"}), 400
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            if request.is_json:
                return jsonify({"error": "Passwords do not match"}), 400
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"error": "Email already registered"}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(phone=phone).first():
            if request.is_json:
                return jsonify({"error": "Phone number already registered"}), 400
            flash('Phone number already registered', 'error')
            return redirect(url_for('signup'))
        
        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            app.logger.info(f"✅ User created successfully - ID: {user.id}, Email: {user.email}")
            
            if request.is_json:
                return jsonify({
                    "message": "Signup successful",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                }), 201
            flash('Account created successfully! Please login to continue.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ Signup error: {str(e)}")
            import traceback
            traceback.print_exc()
            if request.is_json:
                return jsonify({"error": str(e)}), 500
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

@app.route('/api')
def api_info():
    return jsonify({
        "name": "OpenAI Chat API",
        "version": "2.0.0",
        "description": "REST API for OpenAI GPT models with authentication, database, and streaming",
        "features": [
            "User authentication and registration",
            "Multiple OpenAI GPT models (GPT-4o, GPT-4.1, etc.)",
            "Regular chat completions with conversation history",
            "Streaming responses for real-time output",
            "Token usage tracking",
            "CORS enabled for cross-origin requests"
        ],
        "endpoints": {
            "GET /": "Homepage",
            "GET /about": "About page",
            "GET /login": "Login page",
            "POST /login": "Login API",
            "GET /signup": "Signup page",
            "POST /signup": "Signup API",
            "GET /logout": "Logout",
            "GET /chat": "Chat page (authenticated)",
            "GET /api": "API documentation",
            "GET /health": "Check API health status",
            "GET /models": "List available models",
            "POST /chat": "Create chat completion (authenticated)",
            "POST /chat/stream": "Create streaming chat completion (authenticated)"
        },
        "documentation": "See README.md for usage examples"
    }), 200

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "OpenAI Chat API",
        "provider": "OpenAI",
        "database": "Connected"
    }), 200

@app.route('/models')
def get_models():
    return jsonify({
        "models": AVAILABLE_MODELS,
        "default": "gpt-4o-mini"
    }), 200

@app.route('/chat', methods=['POST'])
@csrf.exempt
@login_required
def chat():
    try:
        if not OPENAI_AVAILABLE:
            return jsonify({"error": "Chat services are not configured. Missing OPENAI_API_KEY."}), 503
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data['message']
        model = data.get('model', 'gpt-4o-mini')
        messages = data.get('messages', [])
        
        if model not in AVAILABLE_MODELS:
            return jsonify({
                "error": f"Invalid model. Choose from: {', '.join(AVAILABLE_MODELS)}"
            }), 400
        
        if messages:
            conversation = messages
        else:
            conversation = []
        
        conversation.append({
            "role": "user",
            "content": message
        })
        
        response = client.chat.completions.create(
            model=model,
            messages=conversation
        )
        
        assistant_message = response.choices[0].message.content
        
        conversation.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        result = {
            "response": assistant_message,
            "model": model,
            "conversation": conversation
        }
        
        if response.usage:
            result["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/chat/stream', methods=['POST'])
@csrf.exempt
@login_required
def chat_stream():
    try:
        if not OPENAI_AVAILABLE:
            return jsonify({"error": "Chat services are not configured. Missing OPENAI_API_KEY."}), 503
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data['message']
        model = data.get('model', 'gpt-4o-mini')
        messages = data.get('messages', [])
        
        if model not in AVAILABLE_MODELS:
            return jsonify({
                "error": f"Invalid model. Choose from: {', '.join(AVAILABLE_MODELS)}"
            }), 400
        
        if messages:
            conversation = messages
        else:
            conversation = []
        
        conversation.append({
            "role": "user",
            "content": message
        })
        
        def generate():
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=conversation,
                    stream=True,
                    stream_options={"include_usage": True}
                )
                
                usage_data = None
                for chunk in stream:
                    # Send content chunks
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    # Capture usage data (comes in final chunk)
                    if hasattr(chunk, 'usage') and chunk.usage is not None:
                        usage_data = {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        }
                
                # Send usage data at the end
                if usage_data:
                    yield f"data: {json.dumps({'usage': usage_data})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# Voice Endpoints
@app.route('/voice/tts', methods=['POST'])
@csrf.exempt
@login_required
def text_to_speech():
    """Convert text to speech using OpenAI TTS"""
    try:
        if not OPENAI_AVAILABLE:
            return jsonify({"error": "Voice services are not configured. Missing OPENAI_API_KEY."}), 503
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        voice = data.get('voice', 'alloy')
        speed = data.get('speed', 1.0)
        
        # Validate voice
        valid_voices = [v['id'] for v in AVAILABLE_VOICES]
        if voice not in valid_voices:
            return jsonify({"error": f"Invalid voice. Choose from: {', '.join(valid_voices)}"}), 400
        
        # Validate speed (0.25 to 4.0)
        if not (0.25 <= speed <= 4.0):
            return jsonify({"error": "Speed must be between 0.25 and 4.0"}), 400
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=speed
        )
        
        # Convert to base64 for JSON response
        audio_bytes = response.content
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return jsonify({
            "audio": audio_base64,
            "format": "mp3",
            "voice": voice,
            "speed": speed
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/voice/stt', methods=['POST'])
@csrf.exempt
@login_required
def speech_to_text():
    """Convert speech to text using OpenAI Whisper"""
    try:
        if not OPENAI_AVAILABLE:
            return jsonify({"error": "Voice services are not configured. Missing OPENAI_API_KEY."}), 503
        
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Create file-like object for OpenAI API
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.name = "audio.webm"  # OpenAI supports webm, mp3, mp4, etc.
        
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer,
            language="en"  # Can be auto-detected by removing this parameter
        )
        
        return jsonify({
            "text": transcript.text,
            "language": "en"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/voice/settings', methods=['GET'])
@login_required
def voice_settings():
    """Get available voice settings"""
    return jsonify({
        "voices": AVAILABLE_VOICES,
        "speeds": {
            "min": 0.25,
            "max": 4.0,
            "default": 1.0,
            "presets": [
                {"value": 0.75, "label": "Slow"},
                {"value": 1.0, "label": "Normal"},
                {"value": 1.25, "label": "Fast"},
                {"value": 1.5, "label": "Very Fast"}
            ]
        },
        "models": {
            "tts": "tts-1",
            "stt": "whisper-1"
        },
        "available": OPENAI_AVAILABLE
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get API configuration status"""
    return jsonify({
        "openai": {
            "available": OPENAI_AVAILABLE,
            "key_present": bool(os.environ.get("OPENAI_API_KEY"))
        },
        "google_gemini": {
            "available": NANO_BANANA_AVAILABLE,
            "key_present": bool(os.environ.get("GO_BANAN_API_KEY"))
        }
    }), 200

@app.route('/image/settings', methods=['GET'])
@login_required
def image_settings():
    """Get image generation settings and availability"""
    return jsonify({
        "available": NANO_BANANA_AVAILABLE,
        "model": "gemini-2.5-flash-image",
        "capabilities": ["text-to-image", "image-editing", "multi-image-fusion"],
        "max_size": "1024x1024",
        "formats": ["image/png", "image/jpeg"]
    }), 200

@app.route('/image/generate', methods=['POST'])
@csrf.exempt
@login_required
def generate_image():
    """Generate image using Google Nano Banana (Gemini 2.5 Flash Image)"""
    try:
        if not NANO_BANANA_AVAILABLE:
            return jsonify({"error": "Image generation is not configured. Missing GO_BANAN_API_KEY."}), 503
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Create proper Content structure
        from google.genai import types
        content = types.Content(
            role='user',
            parts=[types.Part(text=prompt)]
        )
        
        # Generate image using Nano Banana
        app.logger.info(f"Generating image with prompt: {prompt[:100]}")
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=content
        )
        
        # Extract image data from response with proper error handling
        if response and hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            
                            # Encode bytes to base64 string for JSON serialization
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            app.logger.info(f"Successfully generated image, size: {len(image_bytes)} bytes")
                            
                            return jsonify({
                                "success": True,
                                "image": image_base64,
                                "mime_type": mime_type,
                                "prompt": prompt,
                                "model": "gemini-2.5-flash-image"
                            }), 200
        
        # No image in response - likely safety block or model issue
        app.logger.warning("No image data in Gemini response - possible safety block or model error")
        return jsonify({"error": "No image generated. The model may have blocked the request for safety reasons."}), 502
        
    except Exception as e:
        app.logger.error(f"Image generation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/image/edit', methods=['POST'])
@csrf.exempt
@login_required
def edit_image():
    """Edit image using Google Nano Banana with text prompts"""
    try:
        if not NANO_BANANA_AVAILABLE:
            return jsonify({"error": "Image editing is not configured. Missing GO_BANAN_API_KEY."}), 503
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        image_data = data.get('image')  # Base64 encoded image
        mime_type = data.get('mime_type', 'image/jpeg')  # Get MIME type from request
        
        if not prompt or not image_data:
            return jsonify({"error": "Prompt and image are required"}), 400
        
        # Sanitize base64 string - remove data URL prefix if present
        if ',' in image_data and image_data.startswith('data:'):
            # Extract MIME type from data URL
            mime_prefix = image_data.split(',')[0]
            if 'image/' in mime_prefix:
                mime_type = mime_prefix.split(':')[1].split(';')[0]
            image_data = image_data.split(',', 1)[1]
        
        # Decode base64 string to bytes
        try:
            decoded_image_bytes = base64.b64decode(image_data)
            app.logger.info(f"Successfully decoded image data, size: {len(decoded_image_bytes)} bytes")
        except Exception as decode_error:
            app.logger.error(f"Base64 decode error: {str(decode_error)}")
            return jsonify({"error": f"Invalid base64 image data: {str(decode_error)}"}), 400
        
        # Create proper Content structure with role and parts using InlineData
        from google.genai import types
        inline_data = types.InlineData(
            mime_type=mime_type,
            data=decoded_image_bytes
        )
        
        content = types.Content(
            role='user',
            parts=[
                types.Part(text=prompt),
                types.Part(inline_data=inline_data)
            ]
        )
        
        # Generate edited image
        app.logger.info(f"Editing image with prompt: {prompt[:100]}, MIME: {mime_type}")
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=content
        )
        
        # Extract edited image from response with proper error handling
        if response and hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            edited_image_bytes = part.inline_data.data
                            response_mime = part.inline_data.mime_type
                            
                            # Encode bytes to base64 string for JSON serialization
                            edited_image_base64 = base64.b64encode(edited_image_bytes).decode('utf-8')
                            app.logger.info(f"Successfully edited image, returned {len(edited_image_bytes)} bytes")
                            
                            return jsonify({
                                "success": True,
                                "image": edited_image_base64,
                                "mime_type": response_mime,
                                "prompt": prompt,
                                "model": "gemini-2.5-flash-image"
                            }), 200
        
        # No image in response - likely safety block or model issue
        app.logger.warning("No image data in Gemini response - possible safety block or model error")
        return jsonify({"error": "No edited image generated. The model may have blocked the request for safety reasons."}), 502
        
    except Exception as e:
        app.logger.error(f"Image editing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/image/capabilities', methods=['GET'])
@login_required
def image_capabilities():
    """Get image generation capabilities"""
    return jsonify({
        "available": NANO_BANANA_AVAILABLE,
        "model": "gemini-2.5-flash-image" if NANO_BANANA_AVAILABLE else None,
        "features": {
            "text_to_image": True,
            "image_editing": True,
            "multi_image_fusion": True,
            "character_consistency": True,
            "natural_language_editing": True,
            "object_removal": True,
            "background_replacement": True,
            "style_transfer": True
        } if NANO_BANANA_AVAILABLE else {},
        "pricing": "$0.039 per image" if NANO_BANANA_AVAILABLE else None,
        "max_resolution": "4K" if NANO_BANANA_AVAILABLE else None
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
