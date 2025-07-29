import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.security_logger import get_security_logger

class RateLimitConfig:
    """
    Rate limiting configuration with memory backend for development.
    Provides configurable rate limits for different endpoints.
    """
    
    def __init__(self):
        self.storage_uri = os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://')
        self.global_limit = os.getenv('RATE_LIMIT_GLOBAL', '100 per hour')
        self.login_limit = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
        self.security_logger = get_security_logger()
    
    def init_limiter(self, app: Flask) -> Limiter:
        """
        Initialize Flask-Limiter with the application.
        
        Args:
            app: Flask application instance
            
        Returns:
            Configured Limiter instance
        """
        def rate_limit_handler(request_limit):
            """Custom handler for rate limit violations."""
            self.security_logger.log_rate_limit_violation('global')
            from flask import jsonify
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later."
            }), 429
        
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=self.storage_uri,
            default_limits=[self.global_limit]
        )
        
        # Initialize with app
        limiter.init_app(app)
        
        return limiter
    
    def get_login_limit(self) -> str:
        """Get the rate limit string for login endpoint."""
        return self.login_limit

# Global rate limit configuration
rate_limit_config = RateLimitConfig()
