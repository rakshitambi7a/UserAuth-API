#!/usr/bin/env python3
"""
Test script for password reset functionality
Tests the complete password reset flow
"""
import sys
import os
import requests
import json
from time import sleep

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_password_reset_flow():
    """Test the complete password reset flow"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Password Reset Flow")
    print("=" * 50)
    
    # Test data
    test_email = "john@example.com"
    new_password = "newpassword123"
    
    # Step 1: Request password reset
    print("\n📧 Step 1: Requesting password reset...")
    
    response = requests.post(f"{base_url}/login", json={
        "email": test_email,
        "password": new_password
    })
    
    if response.status_code == 401:
        print("✓ User exists but password is different (expected)")
    else:
        print(f"ℹ️  Current login status: {response.status_code}")
    
    # Request password reset
    response = requests.post(f"{base_url}/request-password-reset", json={
        "email": test_email
    })
    
    if response.status_code == 200:
        print("✓ Password reset requested successfully")
        print(f"   Response: {response.json().get('message', 'No message')}")
    else:
        print(f"✗ Password reset request failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    # Step 2: Simulate getting token from email (in real scenario, user clicks link)
    print(f"\n🔗 Step 2: Getting reset token...")
    print("   (In a real scenario, the user would get this from the email)")
    print("   Check the console output above for the reset link with token")
    
    # For this test, we'll need to manually extract the token from the email output
    print("   Please check the console output for the email with reset link")
    print("   The token is the part after 'token=' in the URL")
    
    # Step 3: Test token validation
    print(f"\n🔍 Step 3: Testing token validation...")
    
    # This would normally use a real token from the email
    sample_token = "invalid_token_for_testing"
    
    response = requests.post(f"{base_url}/validate-reset-token", json={
        "token": sample_token
    })
    
    print(f"   Token validation response: {response.json()}")
    
    # Step 4: Test password reset with invalid token
    print(f"\n🔐 Step 4: Testing password reset with invalid token...")
    
    response = requests.post(f"{base_url}/reset-password", json={
        "token": sample_token,
        "new_password": new_password
    })
    
    if response.status_code == 400:
        print("✓ Invalid token properly rejected")
    else:
        print(f"   Unexpected response: {response.status_code} - {response.json()}")
    
    print(f"\n✅ Password reset flow test completed!")
    print(f"   To complete the test:")
    print(f"   1. Copy the token from the email output above")
    print(f"   2. Use it in a reset-password request")
    print(f"   3. Try logging in with the new password")
    
    return True

def test_validation_errors():
    """Test validation error cases"""
    base_url = "http://localhost:5000"
    
    print(f"\n🔍 Testing Validation Errors")
    print("=" * 30)
    
    # Test missing email
    response = requests.post(f"{base_url}/request-password-reset", json={})
    if response.status_code == 400:
        print("✓ Missing email properly rejected")
    else:
        print(f"✗ Expected 400, got {response.status_code}")
    
    # Test invalid email format
    response = requests.post(f"{base_url}/request-password-reset", json={
        "email": "invalid-email"
    })
    if response.status_code == 400:
        print("✓ Invalid email format properly rejected")
    else:
        print(f"✗ Expected 400, got {response.status_code}")
    
    # Test missing token
    response = requests.post(f"{base_url}/reset-password", json={
        "new_password": "newpass123"
    })
    if response.status_code == 400:
        print("✓ Missing token properly rejected")
    else:
        print(f"✗ Expected 400, got {response.status_code}")
    
    # Test missing password
    response = requests.post(f"{base_url}/reset-password", json={
        "token": "some-token"
    })
    if response.status_code == 400:
        print("✓ Missing password properly rejected")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

if __name__ == "__main__":
    print("🚀 Starting Password Reset API Tests")
    print("Make sure the Flask app is running on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Test validation errors first
        test_validation_errors()
        
        # Test main flow
        test_password_reset_flow()
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("   Make sure the Flask app is running on http://localhost:5000")
    except KeyboardInterrupt:
        print("\n⏹️  Tests stopped by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
