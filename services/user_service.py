"""
User service layer handling business logic for user operations.
Demonstrates separation of concerns and async operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db.models import User, Client, ServiceProvider, UserRole
from app.schemas.user import ClientCreate, ServiceProviderCreate
from app.core.decorators import log_execution_time


class UserService:
    """
    Service class for user-related operations.
    Encapsulates business logic separate from API layer.
    """
    
    @staticmethod
    @log_execution_time
    async def create_client(db: AsyncSession, client_data: ClientCreate) -> Client:
        """
        Create a new client user.
        
        Args:
            db: Database session
            client_data: Client creation data
            
        Returns:
            Created Client instance
        """
        client = Client(
            email=client_data.email,
            full_name=client_data.full_name,
            phone=client_data.phone,
            user_type=UserRole.CLIENT.value
        )
        
        db.add(client)
        await db.flush()
        await db.refresh(client)
        
        return client
    
    @staticmethod
    @log_execution_time
    async def create_service_provider(
        db: AsyncSession,
        provider_data: ServiceProviderCreate
    ) -> ServiceProvider:
        """
        Create a new service provider user.
        
        Args:
            db: Database session
            provider_data: Service provider creation data
            
        Returns:
            Created ServiceProvider instance
        """
        provider = ServiceProvider(
            email=provider_data.email,
            full_name=provider_data.full_name,
            phone=provider_data.phone,
            service_type=provider_data.service_type,
            user_type=UserRole.SERVICE_PROVIDER.value
        )
        
        db.add(provider)
        await db.flush()
        await db.refresh(provider)
        
        return provider
    
    @staticmethod
    @log_execution_time
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            db: Database session
            user_id: User ID to retrieve
            
        Returns:
            User instance if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    @log_execution_time
    async def get_all_users(db: AsyncSession) -> List[User]:
        """
        Retrieve all users.
        
        Args:
            db: Database session
            
        Returns:
            List of all User instances
        """
        result = await db.execute(select(User))
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def get_clients(db: AsyncSession) -> List[Client]:
        """
        Retrieve all clients.
        
        Args:
            db: Database session
            
        Returns:
            List of Client instances
        """
        result = await db.execute(select(Client))
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def get_service_providers(db: AsyncSession) -> List[ServiceProvider]:
        """
        Retrieve all service providers.
        
        Args:
            db: Database session
            
        Returns:
            List of ServiceProvider instances
        """
        result = await db.execute(select(ServiceProvider))
        return list(result.scalars().all())