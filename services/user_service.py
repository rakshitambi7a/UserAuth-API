"""
User service for business logic operations
Coordinates between controllers and repositories
"""
from typing import Optional, List, Dict, Any
from models.user import User
from repositories.user_repository import UserRepositoryInterface
from utils.validators import validate_email, validate_user_data
from werkzeug.security import generate_password_hash


class UserService:
    """
    Service class handling user business logic
    Separates business logic from data access and web layer
    """

    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Initialize the UserService with a user repository.

        :param user_repository: Repository instance for user data access
        """
        self.user_repository = user_repository

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user with validation and business logic

        :param user_data: Dictionary containing user details
        :return: Result dictionary with user or error
        """
        try:
            # Validate user data
            if not validate_user_data(user_data):
                return {"error": "Invalid user data provided"}
            
            # Check for required fields
            required_fields = ['name', 'email', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    return {"error": f"Missing required field: {field}"}
            
            # Validate email format
            if not validate_email(user_data['email']):
                return {"error": "Invalid email format"}
            
            # Check if user already exists
            existing_user = self.user_repository.find_by_email(user_data['email'])
            if existing_user:
                return {"error": "User with this email already exists"}
            
            # Create user through repository
            user = self.user_repository.create(user_data)
            if user:
                return {"success": True, "user": user.to_dict()}
            else:
                return {"error": "Failed to create user"}
                
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID

        :param user_id: The ID of the user to retrieve
        :return: User object or None if not found
        """
        return self.user_repository.find_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email

        :param email: The email of the user to retrieve
        :return: User object or None if not found
        """
        return self.user_repository.find_by_email(email)

    def update_user(self, user_id: int, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing user's information

        :param user_id: The ID of the user to update
        :param updated_data: Dictionary containing updated user details
        :return: Result dictionary with user or error
        """
        try:
            # Get existing user
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Validate email if being updated
            if 'email' in updated_data:
                if not validate_email(updated_data['email']):
                    return {"error": "Invalid email format"}
                
                # Check if email is already taken by another user
                existing_user = self.user_repository.find_by_email(updated_data['email'])
                if existing_user and existing_user.id != user_id:
                    return {"error": "Email already taken by another user"}
            
            # Update user fields
            user.update_fields(**updated_data)
            
            # Save through repository
            if self.user_repository.update(user):
                return {"success": True, "user": user.to_dict()}
            else:
                return {"error": "Failed to update user"}
                
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        Delete a user by their ID

        :param user_id: The ID of the user to delete
        :return: Result dictionary with success or error message
        """
        try:
            # Check if user exists
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Delete through repository
            if self.user_repository.delete(user_id):
                return {"success": True, "message": "User deleted successfully"}
            else:
                return {"error": "Failed to delete user"}
                
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def list_users(self) -> List[User]:
        """
        Retrieve a list of all users

        :return: List of user objects
        """
        return self.user_repository.find_all()

    def search_users(self, query: str) -> List[User]:
        """
        Search users by name or email

        :param query: Search query string
        :return: List of matching user objects
        """
        if not query or len(query.strip()) < 2:
            return []
        
        return self.user_repository.search(query.strip())

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password

        :param email: User's email
        :param password: User's password
        :return: User object if authentication successful, None otherwise
        """
        user = self.user_repository.find_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user's password with validation

        :param user_id: User's ID
        :param old_password: Current password for verification
        :param new_password: New password to set
        :return: Result dictionary with success or error message
        """
        try:
            # Get user
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Verify old password
            if not user.check_password(old_password):
                return {"error": "Current password is incorrect"}
            
            # Validate new password (basic validation)
            if len(new_password) < 6:
                return {"error": "New password must be at least 6 characters long"}
            
            # Update password
            user.password = generate_password_hash(new_password)
            
            # Save through repository
            if self.user_repository.update(user):
                return {"success": True, "message": "Password changed successfully"}
            else:
                return {"error": "Failed to update password"}
                
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}