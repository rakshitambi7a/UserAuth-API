from werkzeug.security import generate_password_hash, check_password_hash
import hmac

class SecurityUtils:
    """Utility class for security-related operations."""

    @staticmethod
    def hash_password(password):
        """
        Hash a password using Werkzeug's generate_password_hash.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password, hashed_password):
        """
        Verify a password against a hashed password.

        Args:
            password (str): The password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(hashed_password, password)

    @staticmethod
    def generate_hmac(key, message):
        """
        Generate an HMAC for a given message using a secret key.

        Args:
            key (bytes): The secret key.
            message (str): The message to hash.

        Returns:
            str: The generated HMAC in hexadecimal format.
        """
        return hmac.new(key, message.encode('utf-8'), 'sha256').hexdigest()

    @staticmethod
    def verify_hmac(key, message, hmac_to_verify):
        """
        Verify an HMAC against a given message and key.

        Args:
            key (bytes): The secret key.
            message (str): The message to verify.
            hmac_to_verify (str): The HMAC to compare against.

        Returns:
            bool: True if the HMAC matches, False otherwise.
        """
        generated_hmac = SecurityUtils.generate_hmac(key, message)
        return hmac.compare_digest(generated_hmac, hmac_to_verify)
