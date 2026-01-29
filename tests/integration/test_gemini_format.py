#!/usr/bin/env python3
"""
Test Google Gemini API content format fix
"""

import sys
import os
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'family_manager'))

try:
    import google.genai as genai
    print("✅ Using Google GenAI API")

    # Initialize client
    client = genai.Client(api_key="AIzaSyCMxlF2l7-Bc1bwYrmlc7-O5a5-pjevNPY")
    print("✅ API client initialized")

    # Create a simple test prompt (no image needed for basic test)
    test_prompt = "Hello, can you respond with a simple JSON object: {'test': 'success'}"

    # Check available models
    models = client.models.list()
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    print(f"✅ Available Gemini models: {len(gemini_models)}")
    for model in gemini_models[:3]:
        print(f"  - {model.name}")

    # Use first available model
    if gemini_models:
        model_name = gemini_models[0].name
        print(f"✅ Using model: {model_name}")

        # Test basic API call
        response = client.models.generate_content(
            model=model_name,
            contents=[{
                "parts": [
                    {"text": test_prompt}
                ]
            }]
        )
    else:
        print("❌ No Gemini models available")
        sys.exit(1)

    print(f"✅ API response: {response.text[:100]}...")
    print("🎯 Gemini API format is working!")

except Exception as e:
    print(f"❌ API test failed: {e}")
    sys.exit(1)