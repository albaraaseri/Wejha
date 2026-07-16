#!/usr/bin/env python3
"""
Test script to verify Piper TTS models are working
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from twuaqirag.services.text_to_speech import get_tts_service

def test_tts():
    print("🧪 Testing Piper TTS Models")
    print("=" * 60)
    
    # Initialize TTS service
    print("\n1️⃣ Initializing TTS service...")
    tts = get_tts_service()
    print(f"   ✅ Service initialized")
    print(f"   📁 Models directory: {tts.config.models_dir}")
    
    # Test English model
    print("\n2️⃣ Testing English model...")
    try:
        result_en = tts.synthesize_text(
            "Hello! This is a test of the English text to speech system.",
            language="en"
        )
        print(f"   ✅ English synthesis successful!")
        print(f"   📊 Audio size: {len(result_en.audio_data)} bytes")
        print(f"   🎵 Sample rate: {result_en.sample_rate} Hz")
        print(f"   🌍 Language: {result_en.language}")
    except Exception as e:
        print(f"   ❌ English synthesis failed: {e}")
        return False
    
    # Test Arabic model
    print("\n3️⃣ Testing Arabic model...")
    try:
        result_ar = tts.synthesize_text(
            "مرحبا! هذا اختبار لنظام تحويل النص إلى كلام باللغة العربية.",
            language="ar"
        )
        print(f"   ✅ Arabic synthesis successful!")
        print(f"   📊 Audio size: {len(result_ar.audio_data)} bytes")
        print(f"   🎵 Sample rate: {result_ar.sample_rate} Hz")
        print(f"   🌍 Language: {result_ar.language}")
    except Exception as e:
        print(f"   ❌ Arabic synthesis failed: {e}")
        return False
    
    # Test auto-detection
    print("\n4️⃣ Testing automatic language detection...")
    try:
        result_auto_en = tts.synthesize_text(
            "This should be detected as English.",
            language="auto"
        )
        print(f"   ✅ Auto-detected English: {result_auto_en.language}")
        
        result_auto_ar = tts.synthesize_text(
            "هذا يجب أن يتم اكتشافه كعربي.",
            language="auto"
        )
        print(f"   ✅ Auto-detected Arabic: {result_auto_ar.language}")
    except Exception as e:
        print(f"   ❌ Auto-detection failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All TTS tests passed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_tts()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
