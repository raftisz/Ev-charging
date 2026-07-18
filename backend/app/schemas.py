"""
Pydantic schemas used for request validation and response shaping.
Kept separate from SQLModel table models so the API never leaks
internal fields such as password_hash.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str


# ---------- User / Profile ----------

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    wallet_balance: float
    reward_points: int
    dark_mode: bool
    notifications_enabled: bool

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    dark_mode: Optional[bool] = None
    notifications_enabled: Optional[bool] = None


class VehicleCreateRequest(BaseModel):
    make: str
    model: str
    year: Optional[int] = None
    battery_capacity_kwh: float = 75.0
    connector_type: str = "CCS2"
    license_plate: Optional[str] = None


class VehicleResponse(VehicleCreateRequest):
    id: int
    user_id: int
    is_default: bool

    class Config:
        from_attributes = True


# ---------- Stations ----------

class ChargerResponse(BaseModel):
    id: int
    connector_type: str
    power_kw: float
    is_available: bool
    charger_code: str

    class Config:
        from_attributes = True


class StationResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: float
    price_per_kwh: float
    has_fast_charge: bool
    is_open: bool
    opening_hours: str
    amenities: str

    class Config:
        from_attributes = True


class StationDetailResponse(StationResponse):
    chargers: list[ChargerResponse] = []


# ---------- Bookings ----------

class BookingCreateRequest(BaseModel):
    station_id: int
    charger_id: int
    vehicle_id: Optional[int] = None
    reservation_date: str
    reservation_time: str


class BookingResponse(BaseModel):
    id: int
    user_id: int
    station_id: int
    charger_id: int
    vehicle_id: Optional[int] = None
    reservation_date: str
    reservation_time: str
    estimated_cost: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Charging ----------

class ChargingSessionResponse(BaseModel):
    id: int
    booking_id: int
    battery_percent: int
    charging_progress: int
    power_output_kw: float
    charging_speed: str
    remaining_minutes: int
    current_cost: float
    status: str

    class Config:
        from_attributes = True


# ---------- Payments ----------

class PaymentCreateRequest(BaseModel):
    booking_id: Optional[int] = None
    amount: float
    method: str = "credit_card"


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    booking_id: Optional[int] = None
    amount: float
    method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
