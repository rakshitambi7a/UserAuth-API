"""
Improved User model following Single Responsibility Principle
Model only handles data representation, not persistence
"""
from werkzeug.security import check_password_hash
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """
    User model representing user data structure
    Focuses only on data representation and basic validation
    """
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # This will be hashed
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
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
        """
        Create User instance from dictionary
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def update_fields(self, **kwargs) -> None:
        """
        Update user fields and set updated_at timestamp
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':  # Don't allow ID changes
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
