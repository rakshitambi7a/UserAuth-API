"""
Authentication routes with dependency injection and service layer
Handles login and JWT token generation
"""
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.jwt_service import jwt_service
from utils.validators import UserValidator
from utils.security_logger import get_security_logger
from utils.rate_limit import rate_limit_config
from core.container import container

auth_bp = Blueprint('auth', __name__)

def get_user_service():
    """Get user service from dependency injection container"""
    return container.user_service()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with email and password using service layer.
    Returns JWT token on successful authentication.
    Rate limited to 5 attempts per minute.
    """
    security_logger = get_security_logger()
    
    try:
        # Get JSON data from request
        try:
            data = request.get_json()
        except Exception:
            # Handle case where content-type is application/json but no data
            data = None
            
        if not data:
            security_logger.log_authentication_failure("No data provided")
            return jsonify({"error": "No data provided"}), 400
        
        # Extract email and password
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not email:
            security_logger.log_authentication_failure("Email missing")
            return jsonify({"error": "Email is required"}), 400
        
        if not password:
            security_logger.log_authentication_failure("Password missing", email)
            return jsonify({"error": "Password is required"}), 400
        
        # Validate email format
        if not UserValidator.validate_email(email):
            security_logger.log_authentication_failure("Invalid email format", email)
            return jsonify({"error": "Invalid email format"}), 400
        
        # Authenticate user using service layer
        user_service = get_user_service()
        user = user_service.authenticate_user(email, password)
        
        if user:
            # Generate JWT token
            try:
                token = jwt_service.generate_token(user)
                
                return jsonify({
                    "status": "success",
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "token": token,
                    "expires_in": f"{jwt_service.expiration_hours} hours"
                }), 200
                
            except Exception as e:
                security_logger.log_authentication_failure("Token generation failed", email)
                return jsonify({"error": "Authentication succeeded but token generation failed"}), 500
        else:
            # Authentication failed
            security_logger.log_authentication_failure("Invalid credentials", email)
            return jsonify({
                "status": "failed",
                "message": "Invalid email or password"
            }), 401
    
    except Exception as e:
        # Log the error for debugging
        security_logger.log_authentication_failure("Login endpoint error")
        return jsonify({"error": "Internal server error"}), 500
