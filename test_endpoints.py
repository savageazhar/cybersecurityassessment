#!/usr/bin/env python3
"""Test voice and image endpoints through the Flask API"""

import requests
import json
import base64
from io import BytesIO

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("TESTING KIMI AI SERVICES")
print("=" * 60)

# First, we need to get credentials and login
print("\n🔐 Testing Login...")
login_data = {
    "email_or_phone": "downtoearthuser@gmail.com",
    "password": "123456"
}

session = requests.Session()
response = session.post(f"{BASE_URL}/login", json=login_data)

if response.status_code == 200:
    print("✅ Login successful!")
else:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

# Test Voice Settings
print("\n📊 Testing Voice Settings Endpoint...")
response = session.get(f"{BASE_URL}/voice/settings")
if response.status_code == 200:
    settings = response.json()
    print("✅ Voice settings retrieved successfully!")
    print(f"   - Available voices: {len(settings.get('voices', []))}")
    print(f"   - TTS model: {settings.get('models', {}).get('tts')}")
    print(f"   - STT model: {settings.get('models', {}).get('stt')}")
elif response.status_code == 503:
    print("❌ Voice services not configured - OPENAI_API_KEY missing")
else:
    print(f"❌ Failed with status {response.status_code}: {response.text}")

# Test Text-to-Speech
print("\n🔊 Testing Text-to-Speech...")
tts_data = {
    "text": "Hello, this is a test of Kimi AI voice services.",
    "voice": "alloy",
    "speed": 1.0
}
response = session.post(f"{BASE_URL}/voice/tts", json=tts_data)
if response.status_code == 200:
    result = response.json()
    audio_data = result.get('audio', '')
    print(f"✅ TTS works! Generated audio: {len(audio_data)} chars (base64)")
    print(f"   - Format: {result.get('format')}")
    print(f"   - Voice: {result.get('voice')}")
elif response.status_code == 503:
    print("❌ TTS not configured - OPENAI_API_KEY missing or invalid")
else:
    print(f"❌ TTS failed with status {response.status_code}: {response.text}")

# Test Image Generation
print("\n🖼️ Testing Image Generation...")
image_gen_data = {
    "prompt": "A cute red robot waving hello"
}
response = session.post(f"{BASE_URL}/image/generate", json=image_gen_data)
if response.status_code == 200:
    result = response.json()
    image_data = result.get('image', '')
    print(f"✅ Image generation works! Generated image: {len(image_data)} chars (base64)")
    print(f"   - MIME type: {result.get('mime_type')}")
    print(f"   - Model: {result.get('model')}")
elif response.status_code == 503:
    print("❌ Image generation not configured - GO_BANAN_API_KEY missing or invalid")
else:
    print(f"❌ Image generation failed with status {response.status_code}: {response.text}")

# Test Image Settings
print("\n⚙️ Testing Image Settings Endpoint...")
response = session.get(f"{BASE_URL}/image/settings")
if response.status_code == 200:
    settings = response.json()
    print("✅ Image settings retrieved successfully!")
    print(f"   - Model: {settings.get('model')}")
    print(f"   - Available: {settings.get('available')}")
elif response.status_code == 503:
    print("❌ Image services not configured")
else:
    print(f"❌ Failed with status {response.status_code}: {response.text}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
