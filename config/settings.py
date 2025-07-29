"""
Centralized configuration management
Follows the principle of single responsibility for configuration
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class BaseConfig:
    """Base configuration with common settings"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or './users.db'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'users.db'
    
    # Security Configuration
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 1))
    
    # Server Configuration
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Application Configuration
    APP_NAME = os.environ.get('APP_NAME', 'User Management System')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # API Configuration
    API_PREFIX = os.environ.get('API_PREFIX', '/api/v1')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5/minute')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    # Override sensitive defaults for production
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # Must be set in production


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    LOG_LEVEL = 'CRITICAL'  # Suppress logs during testing
    WTF_CSRF_ENABLED = False


def get_config() -> BaseConfig:
    """
    Get configuration based on environment
    """
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Validation function to ensure required config is set
def validate_config(config: BaseConfig) -> bool:
    """
    Validate that required configuration is properly set
    """
    if isinstance(config, ProductionConfig):
        # In production, these must be explicitly set
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing = [var for var in required_vars if not getattr(config, var)]
        
        if missing:
            raise ValueError(f"Required environment variables not set: {missing}")
    
    return True
