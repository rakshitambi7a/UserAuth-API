import re
from typing import Dict, List

class ValidationError(Exception):
    pass

class UserValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> bool:
        return len(password) >= 8
    
    @staticmethod
    def validate_name(name: str) -> bool:
        return len(name.strip()) >= 2
    
    @classmethod
    def validate_user_data(cls, data: Dict) -> List[str]:
        if not isinstance(data, dict):
            raise ValidationError("Input data must be a dictionary")
        
        errors = []
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not name or not cls.validate_name(name):
            errors.append("Name must be at least 2 characters long")
        
        if not email or not cls.validate_email(email):
            errors.append("Invalid email format")
        
        if not password or not cls.validate_password(password):
            errors.append("Password must be at least 8 characters long")
        
        return errors


# Standalone functions for direct import
def validate_email(email: str) -> bool:
    """Validate email format"""
    return UserValidator.validate_email(email)


def validate_user_data(data: Dict) -> bool:
    """Validate user data - returns True if valid, False if invalid"""
    try:
        errors = UserValidator.validate_user_data(data)
        return len(errors) == 0
    except ValidationError:
        return False


def validate_password(password: str) -> bool:
    """Validate password strength"""
    return UserValidator.validate_password(password)


def validate_name(name: str) -> bool:
    """Validate name format"""
    return UserValidator.validate_name(name)