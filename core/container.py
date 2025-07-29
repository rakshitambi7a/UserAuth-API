"""
Dependency injection container for the application
Manages the creation and lifecycle of services and repositories
"""
import os
from dependency_injector import containers, providers
from db.database import Database
from repositories.user_repository import SQLiteUserRepository
from services.user_service import UserService


class ApplicationContainer(containers.DeclarativeContainer):
    """Application container for dependency injection"""
    
    # Configuration
    config = providers.Configuration()
    
    # Database - in testing mode, create new instances each time
    if os.getenv('TESTING') == 'true':
        database = providers.Factory(Database)
    else:
        database = providers.Singleton(Database)
    
    # Repositories
    user_repository = providers.Factory(
        SQLiteUserRepository,
        database=database
    )
    
    # Services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )


# Global container instance
container = ApplicationContainer()
