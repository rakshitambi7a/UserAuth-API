"""
Email service for sending password reset and other notification emails
Supports both SMTP and console (development) email sending
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from utils.security_logger import get_security_logger


class EmailService:
    """
    Email service for sending password reset and notification emails
    Configurable for both development (console) and production (SMTP) use
    """
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.from_name = os.getenv('FROM_NAME', 'User Auth API')
        
        # Use console mode for development if SMTP credentials are not configured
        self.use_console = not (self.smtp_username and self.smtp_password)
        
        self.security_logger = get_security_logger()
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
        """
        Send password reset email with reset link
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: User's name (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Password Reset Request - User Auth API"
        
        # Get base URL for reset link
        base_url = os.getenv('APP_BASE_URL', 'http://localhost:5000')
        reset_url = f"{base_url}/reset-password?token={reset_token}"
        
        # Create email content
        html_content = self._create_password_reset_html(user_name, reset_url)
        text_content = self._create_password_reset_text(user_name, reset_url)
        
        return self._send_email(to_email, subject, text_content, html_content)
    
    def send_password_reset_confirmation(self, to_email: str, user_name: Optional[str] = None) -> bool:
        """
        Send password reset confirmation email
        
        Args:
            to_email: Recipient email address
            user_name: User's name (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Password Reset Successful - User Auth API"
        
        html_content = self._create_password_reset_confirmation_html(user_name)
        text_content = self._create_password_reset_confirmation_text(user_name)
        
        return self._send_email(to_email, subject, text_content, html_content)
    
    def _send_email(self, to_email: str, subject: str, text_content: str, html_content: Optional[str] = None) -> bool:
        """
        Send email using configured method (SMTP or console)
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text email content
            html_content: HTML email content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if self.use_console:
                return self._send_console_email(to_email, subject, text_content)
            else:
                return self._send_smtp_email(to_email, subject, text_content, html_content)
        except Exception as e:
            self.security_logger.log_email_error(to_email, str(e))
            return False
    
    def _send_console_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send email to console for development"""
        print("\n" + "="*60)
        print("📧 EMAIL (Console Mode)")
        print("="*60)
        print(f"To: {to_email}")
        print(f"From: {self.from_name} <{self.from_email}>")
        print(f"Subject: {subject}")
        print("-"*60)
        print(content)
        print("="*60 + "\n")
        
        self.security_logger.log_email_sent(to_email, "console")
        return True
    
    def _send_smtp_email(self, to_email: str, subject: str, text_content: str, html_content: Optional[str] = None) -> bool:
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        
        # Add text content
        msg.attach(MIMEText(text_content, 'plain'))
        
        # Add HTML content if provided
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.smtp_username, self.smtp_password)
        server.send_message(msg)
        server.quit()
        
        self.security_logger.log_email_sent(to_email, "smtp")
        return True
    
    def _create_password_reset_html(self, user_name: Optional[str], reset_url: str) -> str:
        """Create HTML content for password reset email"""
        name_greeting = f"Hello {user_name}" if user_name else "Hello"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333; margin-bottom: 20px;">Password Reset Request</h2>
                
                <p style="color: #555; line-height: 1.6;">{name_greeting},</p>
                
                <p style="color: #555; line-height: 1.6;">
                    You recently requested to reset your password for your User Auth API account. 
                    Click the button below to reset it.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Your Password
                    </a>
                </div>
                
                <p style="color: #555; line-height: 1.6; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{reset_url}" style="color: #007bff; word-break: break-all;">{reset_url}</a>
                </p>
                
                <p style="color: #888; font-size: 12px; margin-top: 30px;">
                    This link will expire in 1 hour for security reasons.<br>
                    If you didn't request this password reset, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _create_password_reset_text(self, user_name: Optional[str], reset_url: str) -> str:
        """Create plain text content for password reset email"""
        name_greeting = f"Hello {user_name}" if user_name else "Hello"
        
        return f"""
{name_greeting},

You recently requested to reset your password for your User Auth API account.

To reset your password, click on the following link:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
User Auth API Team
        """
    
    def _create_password_reset_confirmation_html(self, user_name: Optional[str]) -> str:
        """Create HTML content for password reset confirmation email"""
        name_greeting = f"Hello {user_name}" if user_name else "Hello"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Successful</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #d4edda; padding: 30px; border-radius: 10px; border: 1px solid #c3e6cb;">
                <h2 style="color: #155724; margin-bottom: 20px;">✓ Password Reset Successful</h2>
                
                <p style="color: #155724; line-height: 1.6;">{name_greeting},</p>
                
                <p style="color: #155724; line-height: 1.6;">
                    Your password has been successfully reset. You can now log in with your new password.
                </p>
                
                <p style="color: #6c757d; font-size: 12px; margin-top: 30px;">
                    If you didn't make this change, please contact support immediately.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _create_password_reset_confirmation_text(self, user_name: Optional[str]) -> str:
        """Create plain text content for password reset confirmation email"""
        name_greeting = f"Hello {user_name}" if user_name else "Hello"
        
        return f"""
{name_greeting},

Your password has been successfully reset. You can now log in with your new password.

If you didn't make this change, please contact support immediately.

Best regards,
User Auth API Team
        """


# Global email service instance
email_service = EmailService()
