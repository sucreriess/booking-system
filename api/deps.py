"""
Shared dependencies for API endpoints.
Provides database sessions and authentication.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import verify_api_key


async def get_db_session() -> AsyncSession:
    """
    Dependency to get database session.
    Wrapper around get_db generator for clarity.
    """
    async for session in get_db():
        yield session


async def require_api_key(api_key: str = Depends(verify_api_key)) -> str:
    """
    Dependency to require API key authentication.
    
    Args:
        api_key: Validated API key from verify_api_key dependency
        
    Returns:
        The validated API key
    """
    return api_key