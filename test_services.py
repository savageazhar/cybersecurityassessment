#!/usr/bin/env python3
"""Test script for voice and image services"""

import os
import sys
import base64
from openai import OpenAI

# Test OpenAI Voice Services
print("=" * 60)
print("TESTING OPENAI VOICE SERVICES")
print("=" * 60)

try:
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
    else:
        print(f"✅ OPENAI_API_KEY found: {openai_key[:10]}...")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_key)
        
        # Test TTS
        print("\n📢 Testing Text-to-Speech...")
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input="Hello! This is a test of Kimi AI voice services."
            )
            audio_bytes = response.content
            print(f"✅ TTS works! Generated {len(audio_bytes)} bytes of audio")
        except Exception as e:
            print(f"❌ TTS failed: {str(e)}")
        
        print("\n✅ OpenAI voice services configured correctly!")
        
except Exception as e:
    print(f"❌ OpenAI test failed: {str(e)}")

# Test Google Nano Banana (Gemini Image)
print("\n" + "=" * 60)
print("TESTING GOOGLE NANO BANANA (GEMINI IMAGE)")
print("=" * 60)

try:
    go_banan_key = os.environ.get('GO_BANAN_API_KEY')
    if not go_banan_key:
        print("❌ ERROR: GO_BANAN_API_KEY not found in environment")
    else:
        print(f"✅ GO_BANAN_API_KEY found: {go_banan_key[:10]}...")
        
        # Test Google GenAI
        print("\n🖼️ Testing Image Generation...")
        try:
            import google.genai as genai
            from google.genai import types
            
            # Initialize client
            genai_client = genai.Client(api_key=go_banan_key)
            
            # Test simple image generation
            content = types.Content(
                role='user',
                parts=[types.Part(text="A cute red robot waving hello")]
            )
            
            response = genai_client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=content
            )
            
            # Check response
            if response and hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                image_bytes = part.inline_data.data
                                print(f"✅ Image generation works! Generated {len(image_bytes)} bytes")
                                print("✅ Google Nano Banana configured correctly!")
                                sys.exit(0)
            
            print("❌ No image data in response - possible API issue")
            
        except ImportError as e:
            print(f"❌ Google GenAI library not installed: {str(e)}")
        except Exception as e:
            print(f"❌ Image generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ Google GenAI test failed: {str(e)}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
