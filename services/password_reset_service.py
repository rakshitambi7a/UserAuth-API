"""
Password reset service for handling password reset token generation and validation
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from db.database import Database
from models.user import User
from services.email_service import email_service
from utils.security_logger import get_security_logger
from werkzeug.security import generate_password_hash


class PasswordResetService:
    """
    Service for handling password reset functionality
    Manages reset tokens, email sending, and password updates
    """
    
    def __init__(self):
        self.db = Database()
        self.token_expiry_hours = 1  # Token expires after 1 hour
        self.security_logger = get_security_logger()
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Generate and send password reset token for user
        
        Args:
            email: User's email address
            
        Returns:
            Dict with success/error status and message
        """
        try:
            # Find user by email
            user: Optional[User] = User.find_by_email(email)
            if not user or not user.id:
                # Don't reveal if email exists or not for security
                self.security_logger.log_password_reset_request(email, False, "User not found")
                return {
                    "success": True,  # Always return success to prevent email enumeration
                    "message": "If the email exists in our system, you will receive a password reset link."
                }
            
            # Generate secure reset token
            token = self._generate_reset_token()
            
            # Store token in database
            if not self._store_reset_token(user.id, token):
                self.security_logger.log_password_reset_request(email, False, "Failed to store token")
                return {"error": "Failed to process password reset request"}
            
            # Send reset email
            if email_service.send_password_reset_email(email, token, user.name):
                self.security_logger.log_password_reset_request(email, True)
                return {
                    "success": True,
                    "message": "If the email exists in our system, you will receive a password reset link."
                }
            else:
                self.security_logger.log_password_reset_request(email, False, "Failed to send email")
                return {"error": "Failed to send password reset email"}
                
        except Exception as e:
            self.security_logger.log_password_reset_request(email, False, f"Exception: {str(e)}")
            return {"error": "Internal server error"}
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password using valid token
        
        Args:
            token: Password reset token
            new_password: New password to set
            
        Returns:
            Dict with success/error status and message
        """
        try:
            # Validate token and get user
            user: Optional[User] = self._validate_reset_token(token)
            if not user or not user.email or not user.id:
                self.security_logger.log_password_reset_completion("unknown", False, "Invalid token")
                return {"error": "Invalid or expired reset token"}
            
            # Validate new password
            if len(new_password) < 8:
                self.security_logger.log_password_reset_completion(user.email, False, "Password too short")
                return {"error": "Password must be at least 8 characters long"}
            
            # Update password
            hashed_password = generate_password_hash(new_password)
            if not self._update_user_password(user.id, hashed_password):
                self.security_logger.log_password_reset_completion(user.email, False, "Failed to update password")
                return {"error": "Failed to update password"}
            
            # Mark token as used
            self._mark_token_as_used(token)
            
            # Send confirmation email
            email_service.send_password_reset_confirmation(user.email, user.name)
            
            self.security_logger.log_password_reset_completion(user.email, True)
            return {
                "success": True,
                "message": "Password has been reset successfully"
            }
            
        except Exception as e:
            self.security_logger.log_password_reset_completion("unknown", False, f"Exception: {str(e)}")
            return {"error": "Internal server error"}
    
    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """
        Validate reset token without using it
        
        Args:
            token: Password reset token
            
        Returns:
            Dict with validation status
        """
        try:
            user = self._validate_reset_token(token)
            if user:
                return {
                    "valid": True,
                    "email": user.email
                }
            else:
                return {"valid": False}
                
        except Exception:
            return {"valid": False}
    
    def _generate_reset_token(self) -> str:
        """Generate cryptographically secure reset token"""
        # Generate a 32-character random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        return token
    
    def _store_reset_token(self, user_id: int, token: str) -> bool:
        """Store reset token in database with expiration"""
        try:
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            
            # Clean up old tokens for this user first
            self.db.execute_query(
                "DELETE FROM password_reset_tokens WHERE user_id = ?",
                (user_id,)
            )
            
            # Insert new token
            self.db.execute_query(
                """INSERT INTO password_reset_tokens 
                   (user_id, token, expires_at, used) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, token, expires_at.isoformat(), False)
            )
            
            return True
            
        except Exception:
            return False
    
    def _validate_reset_token(self, token: str) -> Optional[User]:
        """Validate reset token and return associated user if valid"""
        try:
            # Query token from database
            result = self.db.execute_one(
                """SELECT prt.user_id, prt.expires_at, prt.used, u.name, u.email 
                   FROM password_reset_tokens prt
                   JOIN users u ON prt.user_id = u.id
                   WHERE prt.token = ?""",
                (token,)
            )
            
            if not result:
                return None
            
            # Check if token is already used
            if result['used']:
                return None
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(result['expires_at'])
            if datetime.utcnow() > expires_at:
                return None
            
            # Return user object
            user = User(
                user_id=result['user_id'],
                name=result['name'],
                email=result['email']
            )
            
            return user
            
        except Exception:
            return None
    
    def _update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password in database"""
        try:
            self.db.execute_query(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            return True
        except Exception:
            return False
    
    def _mark_token_as_used(self, token: str) -> bool:
        """Mark reset token as used"""
        try:
            self.db.execute_query(
                "UPDATE password_reset_tokens SET used = ? WHERE token = ?",
                (True, token)
            )
            return True
        except Exception:
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired reset tokens from database
        Returns number of tokens cleaned up
        """
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Get count of expired tokens
            result = self.db.execute_one(
                "SELECT COUNT(*) as count FROM password_reset_tokens WHERE expires_at < ? OR used = ?",
                (current_time, True)
            )
            
            count = result['count'] if result else 0
            
            # Delete expired and used tokens
            self.db.execute_query(
                "DELETE FROM password_reset_tokens WHERE expires_at < ? OR used = ?",
                (current_time, True)
            )
            
            return count
            
        except Exception:
            return 0


# Global password reset service instance
password_reset_service = PasswordResetService()
