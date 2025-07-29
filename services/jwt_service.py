import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, g
from models.user import User
from utils.security_logger import get_security_logger

def debug_print(message):
    """Print debug message only if not in testing mode"""
    if not os.getenv('TESTING'):
        print(message)

class JWTService:
    """
    JWT token management service with secure token generation and validation.
    Provides stateless authentication with configurable expiration.
    """
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY', 'default-secret-key'))
        self.algorithm = 'HS256'
        self.expiration_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '1'))
        self.security_logger = get_security_logger()
    
    def generate_token(self, user: User) -> str:
        """
        Generate a JWT token for the authenticated user.
        
        Args:
            user: Authenticated user object
            
        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours)
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            self.security_logger.log_token_event('generated', user.id)
            
            return token
            
        except Exception as e:
            self.security_logger.log_token_event('generation_failed', user.id, str(e))
            raise Exception(f"Token generation failed: {str(e)}")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            debug_print(f"DEBUG: Validating token with secret: {self.secret_key[:10]}...")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            debug_print(f"DEBUG: Token decoded successfully: {payload}")
            
            # Check if token is expired
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                current_time = datetime.utcnow()
                debug_print(f"DEBUG: Token expires at: {exp_datetime}, current time: {current_time}")
                
                if current_time > exp_datetime:
                    debug_print(f"DEBUG: Token has expired")
                    self.security_logger.log_token_event('expired', payload.get('user_id'))
                    return None
            
            self.security_logger.log_token_event('validated', payload.get('user_id'))
            return payload
            
        except jwt.ExpiredSignatureError:
            debug_print(f"DEBUG: JWT ExpiredSignatureError")
            self.security_logger.log_token_event('expired', None, 'Signature expired')
            return None
        except jwt.InvalidTokenError as e:
            debug_print(f"DEBUG: JWT InvalidTokenError: {e}")
            self.security_logger.log_token_event('invalid', None, str(e))
            return None
        except Exception as e:
            debug_print(f"DEBUG: Unexpected error in token validation: {e}")
            self.security_logger.log_token_event('validation_failed', None, str(e))
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user object from a valid JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = self.validate_token(token)
        if not payload:
            return None
        
        try:
            user = User.find_by_id(payload['user_id'])
            return user
        except Exception as e:
            self.security_logger.log_authentication_failure('user_lookup_failed', payload.get('email'))
            return None

# Global JWT service instance
jwt_service = JWTService()

def token_required(f):
    """
    Decorator for routes that require JWT authentication.
    Validates the token and makes user available in Flask's g object.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        debug_print(f"DEBUG: Headers: {dict(request.headers)}")
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        debug_print(f"DEBUG: Authorization header: {auth_header}")
        
        if auth_header:
            try:
                # Expected format: "Bearer <token>"
                parts = auth_header.split(" ")
                debug_print(f"DEBUG: Auth header parts: {parts}")
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
                    debug_print(f"DEBUG: Extracted token: {token[:20]}...")
                else:
                    debug_print(f"DEBUG: Invalid auth header format")
                    return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
            except IndexError:
                debug_print(f"DEBUG: IndexError when parsing auth header")
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        # Check for token in request args (for testing purposes)
        if not token:
            token = request.args.get('token')
            if token:
                debug_print(f"DEBUG: Token found in query params: {token[:20]}...")
        
        if not token:
            debug_print(f"DEBUG: No token found anywhere")
            get_security_logger().log_authentication_failure('missing_token')
            return jsonify({'error': 'Token is missing'}), 401
        
        debug_print(f"DEBUG: About to validate token")
        
        # Validate token and get user
        user = jwt_service.get_user_from_token(token)
        debug_print(f"DEBUG: User from token: {user}")
        
        if not user:
            debug_print(f"DEBUG: Token validation failed")
            get_security_logger().log_authentication_failure('invalid_token')
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        debug_print(f"DEBUG: Token validation successful for user: {user.email}")
        
        # Make user available in request context
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

def optional_token(f):
    """
    Decorator for routes where authentication is optional.
    If token is provided and valid, user is made available in g.current_user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                pass
        
        # Check for token in request args
        if not token:
            token = request.args.get('token')
        
        if token:
            user = jwt_service.get_user_from_token(token)
            g.current_user = user
        else:
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated
