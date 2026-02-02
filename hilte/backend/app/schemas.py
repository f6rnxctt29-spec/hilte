from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    telegram: Optional[str] = None
    address: Optional[str] = None
    status: str = 'active'
    contact: dict[str, Any] = {}
    preferences: dict[str, Any] = {}

class ClientOut(BaseModel):
    id: UUID
    name: str
    status: str
    phone: Optional[str] = None
    telegram: Optional[str] = None
    address: Optional[str] = None
    contact: dict[str, Any]
    preferences: dict[str, Any]
    created_at: datetime

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    contact: Optional[dict[str, Any]] = None
    preferences: Optional[dict[str, Any]] = None

class BookingCreate(BaseModel):
    client_id: Optional[UUID] = None
    object_id: Optional[UUID] = None
    payload: dict[str, Any]
    status: str = 'requested'

class BookingOut(BaseModel):
    id: UUID
    client_id: Optional[UUID] = None
    object_id: Optional[UUID] = None
    payload: dict[str, Any]
    status: str
    created_at: datetime

class BookingUpdate(BaseModel):
    client_id: Optional[UUID] = None
    object_id: Optional[UUID] = None
    payload: Optional[dict[str, Any]] = None
    status: Optional[str] = None

class OrderCreate(BaseModel):
    booking_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    type: Optional[str] = None
    items: list[dict[str, Any]] = []
    price: float = 0
    cost: float = 0
    status: str = 'pending'

class OrderOut(BaseModel):
    id: UUID
    booking_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    type: Optional[str] = None
    items: list[dict[str, Any]]
    price: float
    cost: float
    margin: float
    status: str
    created_at: datetime

class OrderUpdate(BaseModel):
    booking_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    type: Optional[str] = None
    items: Optional[list[dict[str, Any]]] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    status: Optional[str] = None
