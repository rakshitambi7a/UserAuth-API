#!/usr/bin/env python3
"""
Unit tests for validators and core functionality
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_email_validation():
    """Test email validation"""
    from utils.validators import UserValidator
    
    # Valid emails
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "test123@gmail.com",
        "user+tag@example.org"
    ]
    
    # Invalid emails
    invalid_emails = [
        "invalid-email",
        "@domain.com",
        "test@",
        "test.com",
        "",
        "spaces @example.com"
    ]
    
    print("Testing email validation...")
    
    for email in valid_emails:
        assert UserValidator.validate_email(email), f"Valid email failed: {email}"
        print(f"  ✅ {email}")
    
    for email in invalid_emails:
        assert not UserValidator.validate_email(email), f"Invalid email passed: {email}"
        print(f"  ❌ {email} (correctly rejected)")

def test_password_validation():
    """Test password validation"""
    from utils.validators import UserValidator
    
    # Valid passwords (8+ characters)
    valid_passwords = [
        "password123",
        "12345678",
        "longpassword",
        "P@ssw0rd!"
    ]
    
    # Invalid passwords (< 8 characters)
    invalid_passwords = [
        "short",
        "1234567",
        "",
        "a"
    ]
    
    print("\nTesting password validation...")
    
    for password in valid_passwords:
        assert UserValidator.validate_password(password), f"Valid password failed: {password}"
        print(f"  ✅ {password}")
    
    for password in invalid_passwords:
        assert not UserValidator.validate_password(password), f"Invalid password passed: {password}"
        print(f"  ❌ {password} (correctly rejected)")

def test_name_validation():
    """Test name validation"""
    from utils.validators import UserValidator
    
    # Valid names (2+ characters)
    valid_names = [
        "John Doe",
        "Jane",
        "Al",
        "Very Long Name Here"
    ]
    
    # Invalid names (< 2 characters)
    invalid_names = [
        "A",
        "",
        "   ",  # Just spaces
        " "
    ]
    
    print("\nTesting name validation...")
    
    for name in valid_names:
        assert UserValidator.validate_name(name), f"Valid name failed: {name}"
        print(f"  ✅ '{name}'")
    
    for name in invalid_names:
        assert not UserValidator.validate_name(name), f"Invalid name passed: {name}"
        print(f"  ❌ '{name}' (correctly rejected)")

def test_user_data_validation():
    """Test complete user data validation"""
    from utils.validators import UserValidator
    
    print("\nTesting complete user data validation...")
    
    # Valid user data
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    }
    
    errors = UserValidator.validate_user_data(valid_data)
    assert len(errors) == 0, f"Valid data failed validation: {errors}"
    print("  ✅ Valid user data passed")
    
    # Invalid user data
    invalid_data = {
        "name": "A",  # Too short
        "email": "invalid-email",  # Invalid format
        "password": "123"  # Too short
    }
    
    errors = UserValidator.validate_user_data(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got {len(errors)}: {errors}"
    print(f"  ✅ Invalid user data correctly rejected with {len(errors)} errors")

def test_jwt_service():
    """Test JWT service basic functionality"""
    try:
        from services.jwt_service import JWTService
        import os
        
        print("\nTesting JWT service...")
        
        # Set test secret key
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        
        jwt_service = JWTService()
        
        # Test secret key loading
        assert jwt_service.secret_key == 'test-secret-key'
        print("  ✅ JWT secret key loaded correctly")
        
        # Test algorithm
        assert jwt_service.algorithm == 'HS256'
        print("  ✅ JWT algorithm set correctly")
        
        # Test expiration hours
        assert jwt_service.expiration_hours == 1  # Default
        print("  ✅ JWT expiration hours set correctly")
        
    except ImportError as e:
        print(f"  ⚠️  JWT service test skipped: {e}")

def main():
    """Run all unit tests"""
    print("🧪 Running Unit Tests")
    print("=" * 30)
    
    try:
        test_email_validation()
        test_password_validation() 
        test_name_validation()
        test_user_data_validation()
        test_jwt_service()
        
        print("\n🎉 All unit tests passed!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
