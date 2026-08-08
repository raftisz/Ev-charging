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
    role: str
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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)


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
    station_id: int

    class Config:
        from_attributes = True


class ChargerCreateRequest(BaseModel):
    station_id: int
    connector_type: str
    power_kw: float
    is_available: bool = True
    charger_code: str


class ChargerUpdateRequest(BaseModel):
    connector_type: Optional[str] = None
    power_kw: Optional[float] = None
    is_available: Optional[bool] = None
    charger_code: Optional[str] = None


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


class StationCreateRequest(BaseModel):
    name: str
    address: str
    city: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: float = 4.5
    price_per_kwh: float = 8.5
    has_fast_charge: bool = True
    is_open: bool = True
    opening_hours: str = "24 Hours"
    amenities: str = "Wi-Fi, Restroom, Cafe"


class StationUpdateRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    price_per_kwh: Optional[float] = None
    has_fast_charge: Optional[bool] = None
    is_open: Optional[bool] = None
    opening_hours: Optional[str] = None
    amenities: Optional[str] = None


# ---------- Bookings ----------

class BookingCreateRequest(BaseModel):
    station_id: int
    charger_id: int
    vehicle_id: Optional[int] = None
    reservation_date: str
    reservation_time: str


class BookingUpdateRequest(BaseModel):
    reservation_date: Optional[str] = None
    reservation_time: Optional[str] = None
    status: Optional[str] = None
    charger_id: Optional[int] = None
    vehicle_id: Optional[int] = None


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
