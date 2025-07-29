"""
Improved User Service with proper separation of concerns
"""
from typing import Optional, List, Dict, Any
from models.user import User
from utils.validators import UserValidator
from repositories.user_repository import UserRepository


class UserService:
    """Service layer for user operations with business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.validator = UserValidator()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user with validation and business logic
        """
        # Validate input
        errors = self.validator.validate_user_data(user_data)
        if errors:
            return {"success": False, "errors": errors}
        
        # Check if user already exists
        existing_user = self.user_repository.find_by_email(user_data['email'])
        if existing_user:
            return {"success": False, "errors": ["Email already exists"]}
        
        # Create user through repository
        user = self.user_repository.create(user_data)
        
        return {
            "success": True,
            "user": user.to_dict() if user else None
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.find_by_id(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.user_repository.find_all()
    
    def search_users(self, query: str) -> List[User]:
        """Search users by query"""
        return self.user_repository.search(query)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.user_repository.find_by_email(email)
        if user and user.check_password(password):
            return user
        return None
