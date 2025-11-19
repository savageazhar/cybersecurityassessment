import os
from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from flask_cors import CORS
from openai import OpenAI
import json

app = Flask(__name__)
CORS(app)

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

@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        "name": "OpenAI Chat API",
        "version": "1.0.0",
        "description": "REST API for OpenAI GPT models with multiple models, streaming, and token tracking",
        "features": [
            "Multiple OpenAI GPT models (GPT-4o, GPT-4.1, GPT-5, and more)",
            "Regular chat completions with conversation history",
            "Streaming responses for real-time output",
            "Token usage tracking",
            "CORS enabled for cross-origin requests"
        ],
        "endpoints": {
            "GET /": "Web chat interface",
            "GET /api": "API documentation",
            "GET /health": "Check API health status",
            "GET /models": "List available models",
            "POST /chat": "Create chat completion with token usage",
            "POST /chat/stream": "Create streaming chat completion"
        },
        "documentation": "See README.md for usage examples"
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "OpenAI Chat API",
        "provider": "OpenAI"
    }), 200

@app.route('/models', methods=['GET'])
def get_models():
    return jsonify({
        "models": AVAILABLE_MODELS,
        "default": "gpt-4o-mini"
    }), 200

@app.route('/chat', methods=['POST'])
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
