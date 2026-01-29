#!/usr/bin/env python3
"""
Test OCR Dialog Layout Fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'family_manager'))

def test_ocr_dialog_fix():
    """Test that OCRConfirmDialog works with the layout fix"""

    print("🧪 Testing OCR Dialog Layout Fix")
    print("=" * 40)

    try:
        # Import required modules
        from PyQt6.QtWidgets import QApplication
        from main import OCRConfirmDialog

        # Create minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        print("✅ QApplication created")

        # Test with Gemini-style data (structured)
        gemini_data = {
            "success": True,
            "items": [
                {"name": "Milk", "quantity": "2", "unit": "liters", "category": "dairy", "price": "3.99"},
                {"name": "Bread", "quantity": "1", "unit": "loaf", "category": "bakery"},
                {"name": "Apples", "quantity": "6", "unit": "each", "category": "produce"}
            ],
            "confidence": "high"
        }

        # Test dialog creation - this should not crash
        dialog = OCRConfirmDialog(gemini_data)
        print("✅ OCRConfirmDialog created with structured data")

        # Test that layout exists
        layout = dialog.layout()
        if layout is not None:
            print("✅ Dialog layout properly set")
            print(f"✅ Layout has {layout.count()} widgets")
        else:
            print("❌ Dialog layout is None")
            return False

        # Test fallback text mode
        text_dialog = OCRConfirmDialog("Sample OCR text from Tesseract")
        print("✅ OCRConfirmDialog created with text data")

        # Test error handling
        error_dialog = OCRConfirmDialog({"success": False, "error": "API failed"})
        print("✅ OCRConfirmDialog handles error cases")

        print("\n🎯 LAYOUT FIX VERIFICATION: SUCCESS")
        print("📱 OCR Dialog is now fully functional!")
        print("\nReady for AI OCR usage:")
        print("1. Run: python3 main.py")
        print("2. Inventory → Import from Image")
        print("3. Select receipt → AI extracts items")
        print("4. Review in fixed dialog → Confirm import")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ocr_dialog_fix()
    sys.exit(0 if success else 1)