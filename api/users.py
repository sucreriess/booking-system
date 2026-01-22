"""
User API endpoints for registration and retrieval.
Handles client and service provider operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db_session
from app.services.user_service import UserService
from app.schemas.user import (
    ClientCreate,
    ServiceProviderCreate,
    ClientResponse,
    ServiceProviderResponse,
    UserResponse
)
from app.core.decorators import log_request

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
@log_request
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db_session)
) -> ClientResponse:
    """
    Create a new client user.
    
    Args:
        client_data: Client registration data
        db: Database session
        
    Returns:
        Created client details
        
    Raises:
        HTTPException: 400 if email already exists
    """
    try:
        client = await UserService.create_client(db, client_data)
        await db.commit()
        return ClientResponse.model_validate(client)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create client: {str(e)}"
        )


@router.post(
    "/service-providers",
    response_model=ServiceProviderResponse,
    status_code=status.HTTP_201_CREATED
)
@log_request
async def create_service_provider(
    provider_data: ServiceProviderCreate,
    db: AsyncSession = Depends(get_db_session)
) -> ServiceProviderResponse:
    """
    Create a new service provider user.
    
    Args:
        provider_data: Service provider registration data
        db: Database session
        
    Returns:
        Created service provider details
        
    Raises:
        HTTPException: 400 if email already exists
    """
    try:
        provider = await UserService.create_service_provider(db, provider_data)
        await db.commit()
        return ServiceProviderResponse.model_validate(provider)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create service provider: {str(e)}"
        )


@router.get("/clients", response_model=List[ClientResponse])
@log_request
async def get_all_clients(
    db: AsyncSession = Depends(get_db_session)
) -> List[ClientResponse]:
    """
    Retrieve all clients.
    
    Args:
        db: Database session
        
    Returns:
        List of all clients
    """
    clients = await UserService.get_clients(db)
    return [ClientResponse.model_validate(client) for client in clients]


@router.get("/service-providers", response_model=List[ServiceProviderResponse])
@log_request
async def get_all_service_providers(
    db: AsyncSession = Depends(get_db_session)
) -> List[ServiceProviderResponse]:
    """
    Retrieve all service providers.
    
    Args:
        db: Database session
        
    Returns:
        List of all service providers
    """
    providers = await UserService.get_service_providers(db)
    return [ServiceProviderResponse.model_validate(provider) for provider in providers]


@router.get("/{user_id}", response_model=UserResponse)
@log_request
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    Retrieve a specific user by ID.
    
    Args:
        user_id: User ID to retrieve
        db: Database session
        
    Returns:
        User details
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.model_validate(user)


@router.get("/", response_model=List[UserResponse])
@log_request
async def get_all_users(
db: AsyncSession = Depends(get_db_session)
) -> List[UserResponse]:
    """Retrieve all users.
    Args:
    db: Database session
    
Returns:
    List of all users
"""
    users = await UserService.get_all_users(db)
    return [UserResponse.model_validate(user) for user in users]

