"""
Configuration management using Pydantic Settings.
Loads environment variables and provides app-wide configuration.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type safety.
    """
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:mypassword@localhost:5432/local-postgres"
    
    # Security
    API_KEY: str = "default-secret-key-change-in-production"
    
    # Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Appointment Booking System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()