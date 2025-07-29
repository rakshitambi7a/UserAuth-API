"""
User model with proper separation of concerns
Handles only data representation, not persistence or business logic
"""
from werkzeug.security import check_password_hash
from typing import Dict, Any, Optional
from datetime import datetime


class User:
    """
    User model representing user data structure
    Focuses only on data representation and password verification
    """
    
    def __init__(self, user_id=None, name=None, email=None, password=None, created_at=None, updated_at=None):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password  # This will be hashed
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches user's password
        Only handles password verification, not storage
        """
        if not self.password:
            return False
        return check_password_hash(self.password, password)
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation
        Excludes sensitive information by default
        """
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_password and self.password:
            data['password'] = self.password
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            user_id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def update_fields(self, **kwargs) -> None:
        """Update user fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':  # Don't allow ID changes
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()

    # Legacy methods for backward compatibility - will be removed
    @classmethod 
    def find_by_id(cls, user_id):
        """DEPRECATED: Use UserRepository.find_by_id instead"""
        # Late import to avoid circular dependency
        from repositories.user_repository import SQLiteUserRepository
        from db.database import Database
        repo = SQLiteUserRepository(Database())
        return repo.find_by_id(user_id)
    
    @classmethod
    def find_by_email(cls, email):
        """DEPRECATED: Use UserRepository.find_by_email instead"""
        # Late import to avoid circular dependency
        from repositories.user_repository import SQLiteUserRepository
        from db.database import Database
        repo = SQLiteUserRepository(Database())
        return repo.find_by_email(email)
    
    @classmethod
    def get_all(cls):
        """DEPRECATED: Use UserRepository.find_all instead"""
        # Late import to avoid circular dependency
        from repositories.user_repository import SQLiteUserRepository
        from db.database import Database
        repo = SQLiteUserRepository(Database())
        return repo.find_all()
    
    @classmethod
    def search_by_name(cls, name):
        """DEPRECATED: Use UserRepository.search_by_name instead"""
        # Late import to avoid circular dependency
        from repositories.user_repository import SQLiteUserRepository
        from db.database import Database
        repo = SQLiteUserRepository(Database())
        return repo.search_by_name(name)
    
    def save(self):
        """DEPRECATED: Use UserRepository.create or UserRepository.update instead"""
        # Late import to avoid circular dependency
        from repositories.user_repository import SQLiteUserRepository
        from db.database import Database
        repo = SQLiteUserRepository(Database())
        
        if self.id:
            repo.update(self)
        else:
            user = repo.create(self.to_dict(include_password=True))
            if user:
                self.id = user.id
    
    def delete(self):
        """DEPRECATED: Use UserRepository.delete instead"""
        if self.id:
            # Late import to avoid circular dependency
            from repositories.user_repository import SQLiteUserRepository
            from db.database import Database
            repo = SQLiteUserRepository(Database())
            repo.delete(self.id)