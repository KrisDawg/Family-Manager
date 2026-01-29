#!/usr/bin/env python3
"""
Test Google Gemini API connection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'family_manager'))

try:
    import google.genai as genai
    print("✅ Using new Google GenAI API")

    # Test API connection
    client = genai.Client(api_key="AIzaSyCMxlF2l7-Bc1bwYrmlc7-O5a5-pjevNPY")
    print("✅ API client initialized")

    # Test model availability
    models = client.models.list()
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    print(f"✅ Available Gemini models: {len(gemini_models)}")

    print("🎯 Gemini API is ready for OCR!")

except Exception as e:
    print(f"❌ Gemini API test failed: {e}")
    sys.exit(1)