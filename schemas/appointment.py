"""
Pydantic schemas for Appointment entities.
Provides validation and serialization for appointment operations.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.db.models import AppointmentStatus


# ============================================
# APPOINTMENT SCHEMAS
# ============================================

class AppointmentBase(BaseModel):
    """Base appointment schema"""
    appointment_time: datetime
    notes: Optional[str] = Field(None, max_length=500)


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment"""
    client_id: int = Field(..., gt=0)
    service_provider_id: int = Field(..., gt=0)


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[AppointmentStatus] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment responses"""
    id: int
    client_id: int
    service_provider_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    """Detailed appointment response with user information"""
    client_name: Optional[str] = None
    provider_name: Optional[str] = None