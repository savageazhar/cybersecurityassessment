import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from openai import OpenAI
import google.generativeai as genai

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cors = CORS()
openai_client = None
gemini_client = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = 2592000
    app.config['PERMANENT_SESSION_LIFETIME'] = 2592000

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    csrf.init_app(app)
    cors.init_app(app, supports_credentials=True, resources={
        r"/api/*": {"origins": "*"},
        r"/models": {"origins": "*"},
        r"/health": {"origins": "*"}
    })

    global openai_client
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)

    global gemini_client
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        gemini_client = genai.GenerativeModel('gemini-pro')
        app.config['NANO_BANANA_AVAILABLE'] = True
    else:
        app.config['NANO_BANANA_AVAILABLE'] = False

    with app.app_context():
        from . import routes
        routes.register_routes(app)
        db.create_all()

    return app
