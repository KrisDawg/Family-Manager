#!/usr/bin/env python3
"""
Test script for HuggingFace meal generation integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from family_manager.main import HuggingFaceMealPlanner
import json

def test_huggingface_integration():
    """Test HuggingFace meal planner with sample inventory"""

    # Sample inventory data
    inventory_items = [
        {"name": "chicken breast", "qty": 2.0, "unit": "lbs", "category": "protein"},
        {"name": "rice", "qty": 5.0, "unit": "cups", "category": "grains"},
        {"name": "broccoli", "qty": 1.0, "unit": "head", "category": "vegetables"},
        {"name": "eggs", "qty": 12.0, "unit": "count", "category": "protein"},
        {"name": "milk", "qty": 1.0, "unit": "gallon", "category": "dairy"},
        {"name": "bread", "qty": 1.0, "unit": "loaf", "category": "grains"},
        {"name": "banana", "qty": 6.0, "unit": "count", "category": "fruit"}
    ]

    print("🧪 Testing HuggingFace Meal Planner Integration")
    print("=" * 50)

    # Test 1: Initialize planner
    print("Test 1: Initializing HuggingFaceMealPlanner...")
    try:
        planner = HuggingFaceMealPlanner()
        print("✅ Planner initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize planner: {e}")
        return False

    # Test 2: Set test data
    print("\nTest 2: Setting test inventory and parameters...")
    planner.inventory_items = inventory_items
    planner.date = "2024-01-20"
    planner.meal_types = ['breakfast', 'lunch', 'dinner']
    planner.dietary_restrictions = []
    print("✅ Test data set successfully")

    # Test 3: Format inventory
    print("\nTest 3: Testing inventory formatting...")
    try:
        formatted = planner.format_inventory_for_ai()
        print("✅ Inventory formatted successfully")
        print(f"Formatted length: {len(formatted)} characters")
    except Exception as e:
        print(f"❌ Failed to format inventory: {e}")
        return False

    # Test 4: Generate prompt
    print("\nTest 4: Testing prompt generation...")
    try:
        prompt = planner._build_meal_prompt()
        print("✅ Prompt generated successfully")
        print(f"Prompt length: {len(prompt)} characters")
        print("Prompt preview:")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    except Exception as e:
        print(f"❌ Failed to generate prompt: {e}")
        return False

    # Test 5: API Call (optional - may be skipped if API key issues)
    print("\nTest 5: Testing API call (may be skipped if rate limited)...")
    try:
        result = planner.run()
        if result:
            print("✅ API call successful!")
            print(f"Generated meals for: {list(result.keys())}")
            for meal_type, meal_data in result.items():
                if isinstance(meal_data, dict):
                    print(f"  {meal_type}: {meal_data.get('name', 'Unknown')}")
        else:
            print("⚠️ API call returned no results (may be rate limited or key issue)")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("This is expected if API key is invalid or rate limited")

    print("\n" + "=" * 50)
    print("🧪 Test Summary:")
    print("- ✅ HuggingFaceMealPlanner class loads correctly")
    print("- ✅ Inventory formatting works")
    print("- ✅ Prompt generation works")
    print("- ⚠️ API integration may need valid key and network access")

    return True

if __name__ == "__main__":
    success = test_huggingface_integration()
    sys.exit(0 if success else 1)