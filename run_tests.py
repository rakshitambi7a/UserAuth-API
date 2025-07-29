#!/usr/bin/env python3
"""
Test runner for User Management API
Runs all test suites in order
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        success = result.returncode == 0
        if success:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED")
        
        return success
    except Exception as e:
        print(f"💥 Error running {description}: {e}")
        return False

def check_server():
    """Check if server is running"""
    try:
        import requests
        response = requests.get("http://localhost:5009/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all tests"""
    print("🚀 User Management API Test Suite")
    print("=" * 60)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    results = []
    
    # 1. Unit Tests (don't require server)
    success = run_command("python tests/test_unit.py", "Unit Tests")
    results.append(("Unit Tests", success))
    
    # 2. Check if server is running for functional tests
    if check_server():
        print("\n✅ Server is running - proceeding with functional tests")
        
        # 3. Functional Tests (require running server)
        success = run_command("python tests/test_functional.py", "Functional Tests")
        results.append(("Functional Tests", success))
        
        # 4. Security Tests
        success = run_command("python tests/test_security.py", "Security Tests")
        results.append(("Security Tests", success))
        
    else:
        print("\n⚠️  Server not running - skipping functional tests")
        print("   Start server with: python app.py")
        results.append(("Functional Tests", "SKIPPED"))
        results.append(("Security Tests", "SKIPPED"))
    
    # 5. PyTest Tests (if pytest is available)
    try:
        import pytest
        success = run_command("python -m pytest tests/test_basic.py -v", "PyTest Suite")
        results.append(("PyTest Suite", success))
    except ImportError:
        print("\n⚠️  PyTest not available - install with: pip install pytest")
        results.append(("PyTest Suite", "SKIPPED"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}")
            failed += 1
        else:
            print(f"⚠️  {test_name} - {result}")
            skipped += 1
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("🎉 All available tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
