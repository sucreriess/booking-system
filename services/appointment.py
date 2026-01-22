"""
Appointment service layer handling business logic for appointment operations.
Implements CRUD operations and filtering capabilities.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from app.db.models import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.core.decorators import log_execution_time


class AppointmentService:
    """
    Service class for appointment-related operations.
    Encapsulates business logic and data access.
    """
    
    @staticmethod
    @log_execution_time
    async def create_appointment(
        db: AsyncSession,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            db: Database session
            appointment_data: Appointment creation data
            
        Returns:
            Created Appointment instance
        """
        appointment = Appointment(
            client_id=appointment_data.client_id,
            service_provider_id=appointment_data.service_provider_id,
            appointment_time=appointment_data.appointment_time,
            notes=appointment_data.notes,
            status=AppointmentStatus.BOOKED
        )
        
        db.add(appointment)
        await db.flush()
        await db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    @log_execution_time
    async def get_appointment_by_id(
        db: AsyncSession,
        appointment_id: int
    ) -> Optional[Appointment]:
        """
        Retrieve an appointment by ID.
        
        Args:
            db: Database session
            appointment_id: Appointment ID to retrieve
            
        Returns:
            Appointment instance if found, None otherwise
        """
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    @log_execution_time
    async def get_all_appointments(db: AsyncSession) -> List[Appointment]:
        """
        Retrieve all appointments.
        
        Args:
            db: Database session
            
        Returns:
            List of all Appointment instances
        """
        result = await db.execute(select(Appointment))
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def get_appointments_by_user(
        db: AsyncSession,
        user_id: int,
        as_client: bool = True
    ) -> List[Appointment]:
        """
        Retrieve appointments for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            as_client: If True, filter by client_id; otherwise by service_provider_id
            
        Returns:
            List of Appointment instances
        """
        if as_client:
            query = select(Appointment).where(Appointment.client_id == user_id)
        else:
            query = select(Appointment).where(Appointment.service_provider_id == user_id)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def get_appointments_by_date(
        db: AsyncSession,
        date: datetime
    ) -> List[Appointment]:
        """
        Retrieve appointments for a specific date.
        
        Args:
            db: Database session
            date: Date to filter by
            
        Returns:
            List of Appointment instances
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query = select(Appointment).where(
            and_(
                Appointment.appointment_time >= start_of_day,
                Appointment.appointment_time <= end_of_day
            )
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def get_appointments_by_status(
        db: AsyncSession,
        status: AppointmentStatus
    ) -> List[Appointment]:
        """
        Retrieve appointments by status.
        
        Args:
            db: Database session
            status: Status to filter by
            
        Returns:
            List of Appointment instances
        """
        query = select(Appointment).where(Appointment.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    @log_execution_time
    async def update_appointment(
        db: AsyncSession,
        appointment_id: int,
        update_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """
        Update an existing appointment.
        
        Args:
            db: Database session
            appointment_id: ID of appointment to update
            update_data: Update data
            
        Returns:
            Updated Appointment instance if found, None otherwise
        """
        appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
        
        if not appointment:
            return None
        
        # Update fields if provided
        if update_data.appointment_time is not None:
            appointment.appointment_time = update_data.appointment_time
        
        if update_data.notes is not None:
            appointment.notes = update_data.notes
        
        if update_data.status is not None:
            appointment.status = update_data.status
        else:
            # Mark as updated if time changed but status not explicitly set
            if update_data.appointment_time is not None:
                appointment.status = AppointmentStatus.UPDATED
        
        appointment.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    @log_execution_time
    async def cancel_appointment(
        db: AsyncSession,
        appointment_id: int
    ) -> Optional[Appointment]:
        """
        Cancel an appointment.
        
        Args:
            db: Database session
            appointment_id: ID of appointment to cancel
            
        Returns:
            Cancelled Appointment instance if found, None otherwise
        """
        appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
        
        if not appointment:
            return None
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(appointment)
        
        return appointment