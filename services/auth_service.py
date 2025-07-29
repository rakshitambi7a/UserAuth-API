
from werkzeug.security import check_password_hash
from models.user import User
from utils.security_logger import get_security_logger

class AuthService:
    """
    Authentication service with enhanced security logging.
    Handles both hashed and legacy plaintext password authentication.
    """
    
    @staticmethod
    def authenticate(email: str, password: str) -> User | None:
        """
        Authenticate user with email and password.
        Supports both bcrypt hashed and legacy plaintext passwords.
        
        Args:
            email: User email address
            password: User password (plaintext)
            
        Returns:
            User object if authentication successful, None otherwise
        """
        security_logger = get_security_logger()
        
        try:
            user = User.find_by_email(email)
            if not user:
                security_logger.log_login_attempt(email, False, "User not found")
                return None
            
            stored_password = user.password
            
            if not stored_password:
                security_logger.log_login_attempt(email, False, "No password set")
                return None
            
            # Check if password is hashed (starts with pbkdf2:sha256:)
            if stored_password.startswith("pbkdf2:sha256:"):
                # Use Werkzeug's check_password_hash for hashed passwords
                if check_password_hash(stored_password, password):
                    security_logger.log_login_attempt(email, True)
                    return user
                else:
                    security_logger.log_login_attempt(email, False, "Invalid password (hashed)")
                    return None
            else:
                # Legacy plaintext password comparison
                if stored_password == password:
                    security_logger.log_login_attempt(email, True, "Legacy plaintext login")
                    return user
                else:
                    security_logger.log_login_attempt(email, False, "Invalid password (plaintext)")
                    return None
                    
        except Exception as e:
            security_logger.log_authentication_failure("Authentication error", email)
            return None