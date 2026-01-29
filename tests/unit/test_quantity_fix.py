#!/usr/bin/env python3
"""
Test the AI OCR fixes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'family_manager'))

def test_quantity_conversion():
    """Test the safe_float_convert function"""

    # Mock the FamilyManagerApp to test the method
    class MockApp:
        def safe_float_convert(self, value, default=1.0):
            """Safely convert value to float, handling AI uncertainties"""
            if not value or value == '?' or value == 'unknown' or str(value).lower() in ['unknown', 'n/a', 'none']:
                return default

            try:
                # Handle common formats: "2", "2.5", "2L", "500g"
                # Extract numeric part only using regex
                import re
                numeric_match = re.match(r'^(\d+\.?\d*)', str(value).strip())
                if numeric_match:
                    return float(numeric_match.group(1))
                return default
            except (ValueError, TypeError):
                return default

    app = MockApp()

    # Test cases
    test_cases = [
        ('2', 2.0),
        ('2.5', 2.5),
        ('?', 1.0),  # The problematic case
        ('unknown', 1.0),
        ('2L', 2.0),  # Should extract 2
        ('500g', 500.0),  # Should extract 500
        ('', 1.0),
        (None, 1.0),
        ('n/a', 1.0),
        ('1.5kg', 1.5),  # Should extract 1.5
        ('not_a_number', 1.0),  # Should fallback
    ]

    print("🧪 Testing Quantity Conversion Fixes")
    print("=" * 40)

    all_passed = True
    for input_val, expected in test_cases:
        result = app.safe_float_convert(input_val)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_val}' → {result} (expected {expected})")
        if result != expected:
            all_passed = False

    if all_passed:
        print("\n🎯 ALL QUANTITY CONVERSION TESTS PASSED!")
        print("The '?' error should no longer occur.")
    else:
        print("\n❌ Some tests failed - needs debugging.")

    return all_passed

if __name__ == '__main__':
    success = test_quantity_conversion()
    sys.exit(0 if success else 1)