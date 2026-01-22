"""
SQLAlchemy ORM models for Users and Appointments.
Demonstrates OOP principles: inheritance, encapsulation, abstraction.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base


# Enums for type safety
class UserRole(str, Enum):
    """User role enumeration"""
    CLIENT = "client"
    SERVICE_PROVIDER = "service_provider"


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    BOOKED = "booked"
    CANCELLED = "cancelled"
    UPDATED = "updated"


# ============================================
# USER MODELS - OOP IMPLEMENTATION
# ============================================

class User(Base):
    """
    Base User model demonstrating OOP principles.
    Uses Single Table Inheritance pattern via 'user_type' discriminator.
    
    Principles demonstrated:
    - Encapsulation: Data and behavior bundled together
    - Abstraction: Base class for common user attributes
    - Inheritance: Client and ServiceProvider inherit from User
    """
    __tablename__ = "users"
    
    # Polymorphic configuration for inheritance
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "user_type",
        "with_polymorphic": "*"
    }
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Common user attributes
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    user_type = Column(String, nullable=False)  # Discriminator column
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, type={self.user_type})>"


class Client(User):
    """
    Client user type - inherits from User.
    Demonstrates inheritance in OOP.
    """
    __mapper_args__ = {
        "polymorphic_identity": UserRole.CLIENT.value,
    }
    
    # Relationship: A client can have multiple appointments
    appointments = relationship(
        "Appointment",
        back_populates="client",
        foreign_keys="Appointment.client_id"
    )
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, email={self.email})>"


class ServiceProvider(User):
    """
    Service Provider user type - inherits from User.
    Demonstrates inheritance in OOP.
    """
    __mapper_args__ = {
        "polymorphic_identity": UserRole.SERVICE_PROVIDER.value,
    }
    
    # Additional attributes specific to service providers
    service_type = Column(String, nullable=True)
    
    # Relationship: A service provider can have multiple appointments
    appointments = relationship(
        "Appointment",
        back_populates="service_provider",
        foreign_keys="Appointment.service_provider_id"
    )
    
    def __repr__(self) -> str:
        return f"<ServiceProvider(id={self.id}, email={self.email}, service={self.service_type})>"


# ============================================
# APPOINTMENT MODEL
# ============================================

class Appointment(Base):
    """
    Appointment model linking clients and service providers.
    Encapsulates appointment business logic and relationships.
    """
    __tablename__ = "appointments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Appointment details
    appointment_time = Column(DateTime, nullable=False, index=True)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.BOOKED, nullable=False)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="appointments", foreign_keys=[client_id])
    service_provider = relationship(
        "ServiceProvider",
        back_populates="appointments",
        foreign_keys=[service_provider_id]
    )
    
    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, client_id={self.client_id}, provider_id={self.service_provider_id}, status={self.status})>"