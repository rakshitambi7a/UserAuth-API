from flask import Flask
from config.settings import get_config
from routes.user_routes import user_bp
from routes.auth import auth_bp
from utils.rate_limit import rate_limit_config
from utils.security_logger import get_security_logger
import os

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    
    # Initialize security logging
    security_logger = get_security_logger()
    security_logger.log_security_event('application_startup', {'version': '1.0.0'})
    
    # Initialize rate limiting
    try:
        limiter = rate_limit_config.init_limiter(app)
        
        # Apply specific rate limit to login endpoint
        from routes.auth import login
        limiter.limit(rate_limit_config.get_login_limit())(login)
        
        app.logger.info("Rate limiting initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize rate limiting: {e}")
        # Continue without rate limiting in case of error
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    def home():
        """Home route to check if the application is running."""
        return {
            "message": "User Management System API is running and not messy anymore!",
            "status": "healthy",
            "features": {
                "rate_limiting": True,
                "jwt_authentication": True,
                "security_logging": True
            }
        }
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "service": "User Management API",
            "features": {
                "rate_limiting": True,
                "jwt_authentication": True,
                "security_logging": True
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5009))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.run(host=host, port=port, debug=debug)