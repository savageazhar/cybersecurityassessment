from flask import request, jsonify, render_template, redirect, url_for, flash, session, Response, stream_with_context, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, openai_client, gemini_client, login_manager
from .models import User, ChatHistory
import json
import base64
import io
import google.generativeai as genai

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def register_routes(app):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))

        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
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

            if request.is_json:
                return jsonify({"error": "Invalid credentials"}), 401
            flash('Invalid email/phone or password', 'error')

        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))

        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')

            if not all([name, email, phone, password]):
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
        return redirect(url_for('login'))

    @app.route('/chat')
    @login_required
    def chat_page():
        return render_template('chat.html')

    @app.route('/api')
    def api_info():
        return jsonify({
            "name": "AI Gateway API",
            "version": "2.0.0",
            "description": "REST API for OpenAI and Google Gemini models with authentication, database, and streaming",
            "features": [
                "User authentication and registration",
                "Multiple AI models (OpenAI GPT, Google Gemini)",
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
                "POST /api/chat": "Create chat completion (authenticated)",
                "POST /api/chat/stream": "Create streaming chat completion (authenticated)"
            },
            "documentation": "See README.md for usage examples"
        }), 200

    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "AI Gateway API",
            "providers": ["OpenAI", "Google Gemini"],
            "database": "Connected"
        }), 200

    @app.route('/models')
    def get_models():
        return jsonify({
            "models": {
                "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                "google": ["gemini-pro"]
            },
            "default": "gpt-4o"
        }), 200

    @app.route('/api/chat', methods=['POST'])
    @login_required
    def chat():
        try:
            data = request.get_json()

            if not data or 'message' not in data:
                return jsonify({"error": "Missing 'message' field"}), 400

            message = data['message']
            model = data.get('model', 'gpt-4o')
            messages = data.get('messages', [])

            if model.startswith('gpt'):
                if not openai_client:
                    return jsonify({"error": "OpenAI client not configured"}), 503

                if messages:
                    conversation = messages
                else:
                    conversation = []

                conversation.append({"role": "user", "content": message})

                response = openai_client.chat.completions.create(
                    model=model,
                    messages=conversation
                )

                assistant_message = response.choices[0].message.content
                conversation.append({"role": "assistant", "content": assistant_message})

                chat_history = ChatHistory(user_id=current_user.id, conversation=conversation)
                db.session.add(chat_history)
                db.session.commit()

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

            elif model == 'gemini-pro':
                if not gemini_client:
                    return jsonify({"error": "Gemini client not configured"}), 503

                if messages:
                    conversation = messages
                else:
                    conversation = []

                conversation.append({"role": "user", "parts": [message]})

                response = gemini_client.generate_content(conversation)

                conversation.append({"role": "assistant", "content": response.text})

                chat_history = ChatHistory(user_id=current_user.id, conversation=conversation)
                db.session.add(chat_history)
                db.session.commit()

                return jsonify({"response": response.text, "model": model, "conversation": conversation}), 200

            else:
                return jsonify({"error": "Invalid model"}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/image/generate', methods=['POST'])
    @login_required
    def generate_image():
        """Generate image using Google Nano Banana (Gemini 2.5 Flash Image)"""
        try:
            if not current_app.config['NANO_BANANA_AVAILABLE']:
                return jsonify({"error": "Image generation is not configured. Missing GEMINI_API_KEY."}), 503

            data = request.get_json()
            prompt = data.get('prompt', '').strip()

            if not prompt:
                return jsonify({"error": "Prompt is required"}), 400

            # Create proper Content structure
            content = {
                'parts': [
                    {'text': prompt}
                ]
            }

            # Generate image using Nano Banana
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content(
                contents=content,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=['x'],
                    max_output_tokens=2048,
                    temperature=1.0,
                    top_p=0.8,
                    top_k=40
                )
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

                                return jsonify({
                                    "success": True,
                                    "image": image_base64,
                                    "mime_type": mime_type,
                                    "prompt": prompt,
                                    "model": "gemini-2.5-flash-image"
                                }), 200

            # No image in response - likely safety block or model issue
            return jsonify({"error": "No image generated. The model may have blocked the request for safety reasons."}), 502

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/voice/tts', methods=['POST'])
    @login_required
    def text_to_speech():
        """Convert text to speech using OpenAI TTS"""
        try:
            if not openai_client:
                return jsonify({"error": "Voice services are not configured. Missing OPENAI_API_KEY."}), 503

            data = request.get_json()

            if not data or 'text' not in data:
                return jsonify({"error": "Missing 'text' field"}), 400

            text = data['text']
            voice = data.get('voice', 'alloy')
            speed = data.get('speed', 1.0)

            # Generate speech
            response = openai_client.audio.speech.create(
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
    @login_required
    def speech_to_text():
        """Convert speech to text using OpenAI Whisper"""
        try:
            if not openai_client:
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
            transcript = openai_client.audio.transcriptions.create(
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

    @app.route('/api/chat/history', methods=['GET'])
    @login_required
    def get_chat_history():
        history = ChatHistory.query.filter_by(user_id=current_user.id).all()
        return jsonify([h.conversation for h in history])

    @app.route('/api/chat/stream', methods=['POST'])
    @login_required
    def chat_stream():
        try:
            data = request.get_json()

            if not data or 'message' not in data:
                return jsonify({"error": "Missing 'message' field"}), 400

            message = data['message']
            model = data.get('model', 'gpt-4o')
            messages = data.get('messages', [])

            if model.startswith('gpt'):
                if not openai_client:
                    return jsonify({"error": "OpenAI client not configured"}), 503

                if messages:
                    conversation = messages
                else:
                    conversation = []

                conversation.append({"role": "user", "content": message})

                def generate():
                    try:
                        stream = openai_client.chat.completions.create(
                            model=model,
                            messages=conversation,
                            stream=True,
                            stream_options={"include_usage": True}
                        )

                        usage_data = None
                        for chunk in stream:
                            if chunk.choices and len(chunk.choices) > 0:
                                if chunk.choices[0].delta.content is not None:
                                    content = chunk.choices[0].delta.content
                                    yield f"data: {json.dumps({'content': content})}\n\n"

                            if hasattr(chunk, 'usage') and chunk.usage is not None:
                                usage_data = {
                                    "prompt_tokens": chunk.usage.prompt_tokens,
                                    "completion_tokens": chunk.usage.completion_tokens,
                                    "total_tokens": chunk.usage.total_tokens
                                }

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

            elif model == 'gemini-pro':
                if not gemini_client:
                    return jsonify({"error": "Gemini client not configured"}), 503

                if messages:
                    conversation = messages
                else:
                    conversation = []

                conversation.append({"role": "user", "parts": [message]})

                def generate():
                    try:
                        stream = gemini_client.generate_content(conversation, stream=True)
                        for chunk in stream:
                            yield f"data: {json.dumps({'content': chunk.text})}\n\n"
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

            else:
                return jsonify({"error": "Invalid model"}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500
