"""
Repository pattern for User data access
Separates data access logic from business logic
"""
from typing import Optional, List, TYPE_CHECKING
from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash
from db.database import Database

if TYPE_CHECKING:
    from models.user import User


class UserRepositoryInterface(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    def create(self, user_data: dict) -> Optional['User']:
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional['User']:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional['User']:
        pass
    
    @abstractmethod
    def find_all(self) -> List['User']:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List['User']:
        pass
    
    @abstractmethod
    def update(self, user: 'User') -> bool:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class SQLiteUserRepository(UserRepositoryInterface):
    """SQLite implementation of user repository"""
    
    def __init__(self, database: Database):
        self.db = database
    
    def create(self, user_data: dict) -> Optional['User']:
        """Create a new user"""
        try:
            hashed_password = generate_password_hash(user_data['password'])
            
            # Use a single connection for both INSERT and lastrowid
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (user_data['name'], user_data['email'], hashed_password)
                )
                conn.commit()
                
                # Get the last inserted row ID in the same connection
                user_id = cursor.lastrowid
                
                if user_id:
                    return self.find_by_id(user_id)
                return None
            
        except Exception as e:
            # Log error (could use logger here)
            print(f"Error creating user: {e}")
            return None
    
    def find_by_id(self, user_id: int) -> Optional['User']:
        """Find user by ID"""
        result = self.db.execute_one(
            "SELECT * FROM users WHERE id = ?", 
            (user_id,)
        )
        return self._map_to_user(result) if result else None
    
    def find_by_email(self, email: str) -> Optional['User']:
        """Find user by email"""
        result = self.db.execute_one(
            "SELECT * FROM users WHERE email = ?", 
            (email,)
        )
        return self._map_to_user(result) if result else None
    
    def find_all(self) -> List['User']:
        """Get all users"""
        results = self.db.execute_query("SELECT * FROM users")
        return [self._map_to_user(row) for row in results]
    
    def search(self, query: str) -> List['User']:
        """Search users by name or email"""
        search_pattern = f"%{query}%"
        results = self.db.execute_query(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (search_pattern, search_pattern)
        )
        return [self._map_to_user(row) for row in results]
    
    def search_by_name(self, name: str) -> List['User']:
        """Search users by name (for backward compatibility)"""
        search_pattern = f"%{name}%"
        results = self.db.execute_query(
            "SELECT * FROM users WHERE name LIKE ?",
            (search_pattern,)
        )
        return [self._map_to_user(row) for row in results]
    
    def update(self, user: 'User') -> bool:
        """Update user"""
        try:
            self.db.execute_query(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (user.name, user.email, user.id)
            )
            return True
        except Exception:
            return False
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        try:
            self.db.execute_query(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            return True
        except Exception:
            return False
    
    def _map_to_user(self, row) -> 'User':
        """Map database row to User object"""
        # Late import to avoid circular dependency
        from models.user import User
        return User(
            user_id=row['id'],
            name=row['name'], 
            email=row['email'],
            password=row['password']
        )
