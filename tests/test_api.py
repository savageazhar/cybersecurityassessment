import pytest
from unittest.mock import patch, MagicMock
import io

def test_chat_success(auth_client):
    with patch('app.openai_client.chat.completions.create') as mock_create:
        # Mock the response from OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello there!"))]
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_create.return_value = mock_response

        response = auth_client.post('/api/chat', json={
            'message': 'Hello',
            'model': 'gpt-4o'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == "Hello there!"
        assert data['model'] == "gpt-4o"
        assert 'conversation' in data

        # Verify OpenAI client was called correctly
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args['model'] == 'gpt-4o'
        assert call_args['messages'][0]['content'] == 'Hello'

def test_chat_missing_message(auth_client):
    response = auth_client.post('/api/chat', json={})
    assert response.status_code == 400
    assert b"Missing 'message' field" in response.data

def test_chat_invalid_model(auth_client):
    response = auth_client.post('/api/chat', json={
        'message': 'Hello',
        'model': 'invalid-model'
    })
    assert response.status_code == 400
    assert b"Invalid model" in response.data

def test_voice_tts(auth_client):
    with patch('app.routes.openai_client.audio.speech.create') as mock_create:
        mock_response = MagicMock()
        mock_response.content = b"fake_audio_bytes"
        mock_create.return_value = mock_response

        response = auth_client.post('/voice/tts', json={
            'text': 'Hello world',
            'voice': 'alloy',
            'speed': 1.0
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'audio' in data
        assert data['voice'] == 'alloy'

        mock_create.assert_called_once()

def test_voice_stt(auth_client):
    with patch('app.routes.openai_client.audio.transcriptions.create') as mock_create:
        mock_create.return_value = MagicMock(text="Transcribed text")

        data = {
            'audio': (io.BytesIO(b"fake_audio_content"), 'test.webm')
        }

        response = auth_client.post('/voice/stt', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == "Transcribed text"

        mock_create.assert_called_once()

def test_image_generate(auth_client):
    with patch('app.routes.genai.GenerativeModel') as mock_genai:
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data.data = b"fake_image_bytes"
        mock_part.inline_data.mime_type = "image/jpeg"
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_genai.return_value.generate_content.return_value = mock_response

        response = auth_client.post('/image/generate', json={
            'prompt': 'A cute cat'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'image' in data
        assert data['prompt'] == 'A cute cat'

def test_image_generate_unavailable(auth_client, app):
    with app.app_context():
        app.config['NANO_BANANA_AVAILABLE'] = False
        response = auth_client.post('/image/generate', json={
            'prompt': 'A cute cat'
        })
        assert response.status_code == 503
        assert b"Image generation is not configured" in response.data

def test_gemini_chat_success(auth_client):
    with patch('app.gemini_client.generate_content') as mock_generate:
        mock_generate.side_effect = Exception("400 API key not valid.")
        response = auth_client.post('/api/chat', json={
            'message': 'Hello',
            'model': 'gemini-pro'
        })
        assert response.status_code == 500
        data = response.get_json()
        assert "400 API key not valid." in data['error']

def test_gemini_chat_stream_success(auth_client):
    with patch('app.gemini_client.generate_content') as mock_generate:
        mock_generate.side_effect = Exception("400 API key not valid.")
        response = auth_client.post('/api/chat/stream', json={
            'message': 'Hello',
            'model': 'gemini-pro'
        })
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        lines = response.data.decode().split('\n')
        assert any("API key not valid" in line for line in lines)
