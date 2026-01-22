"""
Database session management using async SQLAlchemy.
Demonstrates generator pattern for dependency injection.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.db.database import engine
from typing import AsyncGenerator


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function providing database sessions.
    Demonstrates generator pattern for resource management.
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        Used as FastAPI dependency for automatic session management
        and cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()