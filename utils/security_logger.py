import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g
from functools import wraps

class SecurityLogger:
    """
    Structured security event logging with request context.
    Provides JSON-formatted logs for security monitoring and audit trails.
    """
    
    def __init__(self, log_file: str = None, log_level: str = "INFO"):
        self.logger = logging.getLogger('security')
        
        # Suppress logging during tests
        if os.getenv('TESTING'):
            self.logger.setLevel(logging.CRITICAL)  # Only show critical errors during tests
        else:
            self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler if log_file is specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            self.logger.addHandler(file_handler)
        
        self.logger.addHandler(console_handler)
        
        # Custom formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Extract request context for logging."""
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': None,
            'user_agent': None,
            'endpoint': None,
            'method': None,
            'user_id': None
        }
        
        try:
            if request:
                context.update({
                    'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                    'user_agent': request.headers.get('User-Agent', 'Unknown'),
                    'endpoint': request.endpoint,
                    'method': request.method
                })
                
                # Get user ID if available in Flask's g object
                if hasattr(g, 'current_user') and g.current_user:
                    context['user_id'] = getattr(g.current_user, 'id', None)
        except RuntimeError:
            # Outside of request context
            pass
        
        return context
    
    def log_security_event(self, event_type: str, details: Dict[str, Any] = None, level: str = "INFO"):
        """
        Log a security event with structured data.
        
        Args:
            event_type: Type of security event (e.g., 'login_attempt', 'rate_limit_violation')
            details: Additional event-specific details
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_data = {
            'event_type': event_type,
            'context': self._get_request_context(),
            'details': details or {}
        }
        
        log_message = json.dumps(log_data, default=str)
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, log_message)
    
    def log_login_attempt(self, email: str, success: bool, failure_reason: str = None):
        """Log login attempt with outcome."""
        details = {
            'email': email,
            'success': success,
            'failure_reason': failure_reason
        }
        
        level = "INFO" if success else "WARNING"
        self.log_security_event('login_attempt', details, level)
    
    def log_rate_limit_violation(self, limit_type: str, email: str = None):
        """Log rate limit violation."""
        details = {
            'limit_type': limit_type,
            'email': email
        }
        
        self.log_security_event('rate_limit_violation', details, "WARNING")
    
    def log_token_event(self, event: str, user_id: int = None, reason: str = None):
        """Log JWT token events (generation, validation, expiration)."""
        details = {
            'token_event': event,
            'user_id': user_id,
            'reason': reason
        }
        
        level = "INFO" if event == "generated" else "WARNING"
        self.log_security_event('token_event', details, level)
    
    def log_authentication_failure(self, reason: str, email: str = None):
        """Log authentication failures."""
        details = {
            'reason': reason,
            'email': email
        }
        
        self.log_security_event('authentication_failure', details, "WARNING")

# Global security logger instance
def get_security_logger() -> SecurityLogger:
    """Get or create security logger instance."""
    if not hasattr(get_security_logger, '_instance'):
        log_file = os.getenv('LOG_FILE', 'security.log') if os.getenv('ENABLE_SECURITY_LOGGING', 'true').lower() == 'true' else None
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        get_security_logger._instance = SecurityLogger(log_file, log_level)
    
    return get_security_logger._instance

def log_security_event(event_type: str, details: Dict[str, Any] = None, level: str = "INFO"):
    """Convenience function for logging security events."""
    logger = get_security_logger()
    logger.log_security_event(event_type, details, level)
