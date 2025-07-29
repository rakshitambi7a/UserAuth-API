#!/usr/bin/env python3
"""
Test script to demonstrate the new security features:
- Rate Limiting
- JWT Authentication
- Security Logging
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:5009"

def test_rate_limiting():
    """Test rate limiting on login endpoint."""
    print("🔒 Testing Rate Limiting...")
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Try to make 6 requests (should trigger rate limit after 5)
    for i in range(6):
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"  Attempt {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print("  ✅ Rate limit triggered successfully!")
            break
    else:
        print("  ⚠️  Rate limit not triggered (may need to wait or adjust timing)")

def test_jwt_authentication():
    """Test JWT token generation and usage."""
    print("\n🎫 Testing JWT Authentication...")
    
    # First, create a test user (if not exists)
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    # Try to create user
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    if response.status_code in [201, 400]:  # 400 if user already exists
        print("  ✅ Test user ready")
    
    # Login to get JWT token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"  ✅ Login successful, token generated")
        
        # Test protected route
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        
        if response.status_code == 200:
            print("  ✅ Protected route access successful")
        else:
            print(f"  ❌ Protected route failed: {response.status_code}")
    else:
        print(f"  ❌ Login failed: {response.status_code}")

def test_security_logging():
    """Check if security logging is working."""
    print("\n📝 Testing Security Logging...")
    
    log_file = "security.log"
    
    # Make a request to generate logs
    requests.get(f"{BASE_URL}/")
    
    if os.path.exists(log_file):
        print("  ✅ Security log file exists")
        
        # Check recent logs
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                print(f"  ✅ Found {len(lines)} log entries")
                print(f"  Latest entry: {lines[-1].strip()}")
            else:
                print("  ⚠️  Log file exists but is empty")
    else:
        print("  ⚠️  Security log file not found")

def main():
    print("🧪 Testing Security Features")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start with: python app.py")
        return
    
    # Run tests
    test_rate_limiting()
    test_jwt_authentication()
    test_security_logging()
    
    print("\n" + "=" * 40)
    print("🏁 Security testing complete!")
    print("Check security.log for detailed security events.")

if __name__ == "__main__":
    main()
