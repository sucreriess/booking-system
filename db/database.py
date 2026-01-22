"""
Database engine and base class setup.
Configures async SQLAlchemy engine for PostgreSQL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Base class for all models
Base = declarative_base()