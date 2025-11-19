import os
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, validate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

CORS(app)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY_CYB_SEC")
)

AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-3.5-turbo"
]

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
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
        if not request.is_json:
            try:
                validate_csrf(request.form.get('csrf_token'))
            except Exception as e:
                flash('CSRF validation failed. Please try again.', 'error')
                return redirect(url_for('login'))
        
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
            login_user(user)
            if request.is_json:
                return jsonify({
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                }), 200
            return redirect(url_for('chat_page'))
        
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
        if not request.is_json:
            try:
                validate_csrf(request.form.get('csrf_token'))
            except Exception as e:
                flash('CSRF validation failed. Please try again.', 'error')
                return redirect(url_for('signup'))
        
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        
        if not all([name, email, phone, password]):
            if request.is_json:
                return jsonify({"error": "All fields are required"}), 400
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"error": "Email already registered"}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            
            if request.is_json:
                return jsonify({
                    "message": "Signup successful",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                }), 201
            flash('Account created successfully!', 'success')
            return redirect(url_for('chat_page'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({"error": str(e)}), 500
            flash('An error occurred. Please try again.', 'error')
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
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
