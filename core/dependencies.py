"""
Dependency injection container for better separation of concerns
Manages object creation and dependencies
"""
from typing import Dict, Any, Callable
from db.database import Database
from repositories.user_repository import SQLiteUserRepository, UserRepositoryInterface
from services.improved_user_service import UserService
from config.settings import get_config


class DIContainer:
    """
    Simple dependency injection container
    Helps manage object lifecycle and dependencies
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        
        # Register default factories
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default service factories"""
        self.register_factory('config', lambda: get_config())
        self.register_factory('database', lambda: Database())
        self.register_factory('user_repository', 
                            lambda: SQLiteUserRepository(self.get('database')))
        self.register_factory('user_service', 
                            lambda: UserService(self.get('user_repository')))
    
    def register_singleton(self, name: str, instance: Any):
        """Register a singleton instance"""
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function for creating instances"""
        self._factories[name] = factory
    
    def register_service(self, name: str, service: Any):
        """Register a service instance"""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """Get a service by name"""
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check registered services
        if name in self._services:
            return self._services[name]
        
        # Create from factory
        if name in self._factories:
            instance = self._factories[name]()
            # Store as singleton for future use
            self._singletons[name] = instance
            return instance
        
        raise ValueError(f"Service '{name}' not found")
    
    def clear(self):
        """Clear all services (useful for testing)"""
        self._services.clear()
        self._singletons.clear()


# Global container instance
container = DIContainer()


def get_user_service() -> UserService:
    """Convenience function to get user service"""
    return container.get('user_service')


def get_user_repository() -> UserRepositoryInterface:
    """Convenience function to get user repository"""
    return container.get('user_repository')


def get_database() -> Database:
    """Convenience function to get database"""
    return container.get('database')
