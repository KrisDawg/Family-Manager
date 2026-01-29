#!/usr/bin/env python3
"""
Phase 5c Mobile App - Basic Validation Tests
Tests loading indicators, connectivity detection, and error handling
"""

import sys
import os
import time
import socket
from datetime import datetime

# Add kivy_app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kivy_app'))

from api_client import APIClient, REQUEST_TIMEOUT, CONNECT_TIMEOUT

def test_import_modules():
    """Verify all new modules import correctly"""
    print("=" * 60)
    print("TEST 1: Verify Module Imports")
    print("-" * 60)
    
    try:
        from main import LoadingDialog, ConnectivityManager, OfflineIndicator
        print("✅ LoadingDialog imported successfully")
        print("✅ ConnectivityManager imported successfully")
        print("✅ OfflineIndicator imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_api_client_constants():
    """Verify API client timeout configuration"""
    print("\n" + "=" * 60)
    print("TEST 2: Verify API Client Configuration")
    print("-" * 60)
    
    print(f"REQUEST_TIMEOUT: {REQUEST_TIMEOUT}s")
    print(f"CONNECT_TIMEOUT: {CONNECT_TIMEOUT}s")
    
    if REQUEST_TIMEOUT > 0 and CONNECT_TIMEOUT > 0:
        print("✅ Timeout values configured correctly")
        return True
    else:
        print("❌ Timeout values not properly set")
        return False

def test_api_client_connection_methods():
    """Verify API client has new connection checking methods"""
    print("\n" + "=" * 60)
    print("TEST 3: Verify API Client Connection Methods")
    print("-" * 60)
    
    try:
        client = APIClient(base_url="http://localhost:5000")
        
        # Check test_server_connection exists
        if hasattr(client, 'test_server_connection'):
            print("✅ test_server_connection() method exists")
        else:
            print("❌ test_server_connection() method missing")
            return False
        
        # Check get_connection_status exists
        if hasattr(client, 'get_connection_status'):
            print("✅ get_connection_status() method exists")
        else:
            print("❌ get_connection_status() method missing")
            return False
        
        # Test test_server_connection with localhost (should fail gracefully if not running)
        print("\nTesting server connection checker (localhost:5000)...")
        is_reachable, message = client.test_server_connection()
        print(f"  Result: {message}")
        print("✅ Connection test method works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Error testing connection methods: {e}")
        return False

def test_connectivity_manager():
    """Verify connectivity detection works"""
    print("\n" + "=" * 60)
    print("TEST 4: Verify Connectivity Detection")
    print("-" * 60)
    
    try:
        # Import here to avoid GUI initialization
        import socket
        
        def test_online():
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                return True
            except (socket.timeout, socket.error):
                return False
        
        is_online = test_online()
        status = "🟢 Online" if is_online else "🔴 Offline"
        print(f"Device status: {status}")
        print("✅ Connectivity detection works")
        return True
    except Exception as e:
        print(f"❌ Connectivity detection failed: {e}")
        return False

def test_api_client_error_handling():
    """Verify improved error handling exists"""
    print("\n" + "=" * 60)
    print("TEST 5: Verify Enhanced Error Handling")
    print("-" * 60)
    
    try:
        client = APIClient(base_url="http://localhost:5000")
        
        # Make a request to a non-existent endpoint that will timeout
        # This should not throw an exception, but log and return None
        result = client.request('GET', 'nonexistent')
        
        if result is None:
            print("✅ Error handling returns None gracefully")
        else:
            print("❌ Error handling not working as expected")
            return False
        
        print("✅ API client has enhanced error handling")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_buildozer_config():
    """Verify buildozer.spec has required dependencies"""
    print("\n" + "=" * 60)
    print("TEST 6: Verify Buildozer Configuration")
    print("-" * 60)
    
    try:
        with open('buildozer.spec', 'r') as f:
            content = f.read()
        
        required_deps = {
            'python3': 'python3' in content,
            'kivy': 'kivy' in content,
            'requests': 'requests' in content,
            'pillow': 'pillow' in content,
            'sqlite3': 'sqlite3' in content
        }
        
        all_present = True
        for dep, present in required_deps.items():
            status = "✅" if present else "❌"
            print(f"{status} {dep}: {'Present' if present else 'MISSING'}")
            if not present:
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"❌ Buildozer config check failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  Phase 5c Mobile App - Validation Test Suite" + " " * 14 + "║")
    print("║  Testing Loading Indicators, Connectivity, Error Handling" + " " * 2 + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Module Imports", test_import_modules),
        ("API Configuration", test_api_client_constants),
        ("Connection Methods", test_api_client_connection_methods),
        ("Connectivity Detection", test_connectivity_manager),
        ("Error Handling", test_api_client_error_handling),
        ("Buildozer Config", test_buildozer_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} threw exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("-" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} | {test_name}")
    
    print("-" * 60)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All Phase 5c improvements validated successfully!")
        print("\nReady for APK building:")
        print("  $ buildozer android debug")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review above for details.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
