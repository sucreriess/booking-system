"""
Pydantic schemas for User entities.
Provides validation and serialization for API requests/responses.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.db.models import UserRole


# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class ClientCreate(UserBase):
    """Schema for creating a new client"""
    pass


class ServiceProviderCreate(UserBase):
    """Schema for creating a new service provider"""
    service_type: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    user_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientResponse(UserResponse):
    """Schema for client responses"""
    pass


class ServiceProviderResponse(UserResponse):
    """Schema for service provider responses"""
    service_type: Optional[str] = None