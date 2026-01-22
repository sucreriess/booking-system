"""
Appointment API endpoints for CRUD operations.
Includes filtering by user, date, and status.
Protected routes require API key authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_db_session, require_api_key
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.db.models import AppointmentStatus
from app.core.decorators import log_request
from app.api.websocket import manager

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@log_request
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db_session)
) -> AppointmentResponse:
    """
    Create a new appointment.
    
    Args:
        appointment_data: Appointment creation data
        db: Database session
        
    Returns:
        Created appointment details
        
    Raises:
        HTTPException: 400 if creation fails
    """
    try:
        appointment = await AppointmentService.create_appointment(db, appointment_data)
        await db.commit()
        
        # Broadcast WebSocket event
        await manager.broadcast_appointment_event(
            event_type="appointment_booked",
            appointment_data={
                "id": appointment.id,
                "client_id": appointment.client_id,
                "service_provider_id": appointment.service_provider_id,
                "appointment_time": appointment.appointment_time.isoformat(),
                "status": appointment.status.value
            }
        )
        
        return AppointmentResponse.model_validate(appointment)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create appointment: {str(e)}"
        )


@router.get("/", response_model=List[AppointmentResponse])
@log_request
async def get_appointments(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    as_client: bool = Query(True, description="Filter as client (True) or provider (False)"),
    date: Optional[datetime] = Query(None, description="Filter by date"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db_session)
) -> List[AppointmentResponse]:
    """
    Retrieve appointments with optional filtering.
    
    Args:
        user_id: Optional user ID to filter by
        as_client: Whether to filter as client or service provider
        date: Optional date to filter by
        status: Optional status to filter by
        db: Database session
        
    Returns:
        List of appointments matching filters
    """
    # Apply filters based on query parameters
    if user_id:
        appointments = await AppointmentService.get_appointments_by_user(
            db, user_id, as_client
        )
    elif date:
        appointments = await AppointmentService.get_appointments_by_date(db, date)
    elif status:
        appointments = await AppointmentService.get_appointments_by_status(db, status)
    else:
        appointments = await AppointmentService.get_all_appointments(db)
    
    return [AppointmentResponse.model_validate(apt) for apt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
@log_request
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> AppointmentResponse:
    """
    Retrieve a specific appointment by ID.
    
    Args:
        appointment_id: Appointment ID to retrieve
        db: Database session
        
    Returns:
        Appointment details
        
    Raises:
        HTTPException: 404 if appointment not found
    """
    appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    
    return AppointmentResponse.model_validate(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
@log_request
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(require_api_key)  # Protected route
) -> AppointmentResponse:
    """
    Update an existing appointment.
    Requires API key authentication.
    
    Args:
        appointment_id: Appointment ID to update
        update_data: Update data
        db: Database session
        api_key: Validated API key
        
    Returns:
        Updated appointment details
        
    Raises:
        HTTPException: 404 if appointment not found
    """
    appointment = await AppointmentService.update_appointment(
        db, appointment_id, update_data
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    
    await db.commit()
    
    # Broadcast WebSocket event
    await manager.broadcast_appointment_event(
        event_type="appointment_updated",
        appointment_data={
            "id": appointment.id,
            "client_id": appointment.client_id,
            "service_provider_id": appointment.service_provider_id,
            "appointment_time": appointment.appointment_time.isoformat(),
            "status": appointment.status.value
        }
    )
    
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", response_model=AppointmentResponse)
@log_request
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(require_api_key)  # Protected route
) -> AppointmentResponse:
    """
    Cancel an appointment.
    Requires API key authentication.
    
    Args:
        appointment_id: Appointment ID to cancel
        db: Database session
        api_key: Validated API key
        
    Returns:
        Cancelled appointment details
        
    Raises:
        HTTPException: 404 if appointment not found
    """
    appointment = await AppointmentService.cancel_appointment(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    
    await db.commit()
    
    # Broadcast WebSocket event
    await manager.broadcast_appointment_event(
        event_type="appointment_cancelled",
        appointment_data={
            "id": appointment.id,
            "client_id": appointment.client_id,
            "service_provider_id": appointment.service_provider_id,
            "appointment_time": appointment.appointment_time.isoformat(),
            "status": appointment.status.value
        }
    )
    
    return AppointmentResponse.model_validate(appointment)