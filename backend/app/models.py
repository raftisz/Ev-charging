"""
SQLModel table definitions.
Each class is both a Pydantic model (validation) and an ORM table (SQLModel).
"""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = None
    password_hash: str
    avatar_url: Optional[str] = None
    wallet_balance: float = Field(default=0.0)
    reward_points: int = Field(default=0)
    dark_mode: bool = Field(default=True)
    notifications_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    make: str
    model: str
    year: Optional[int] = None
    battery_capacity_kwh: float = Field(default=75.0)
    connector_type: str = Field(default="CCS2")
    license_plate: Optional[str] = None
    is_default: bool = Field(default=True)


class Station(SQLModel, table=True):
    __tablename__ = "stations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str
    city: str = Field(default="Bangkok")
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: float = Field(default=4.5)
    price_per_kwh: float = Field(default=8.5)
    has_fast_charge: bool = Field(default=True)
    is_open: bool = Field(default=True)
    opening_hours: str = Field(default="24 Hours")
    amenities: str = Field(default="Wi-Fi, Restroom, Cafe")


class Charger(SQLModel, table=True):
    __tablename__ = "chargers"

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(foreign_key="stations.id", index=True)
    connector_type: str = Field(default="CCS2")
    power_kw: float = Field(default=60.0)
    is_available: bool = Field(default=True)
    charger_code: str = Field(default="A1")


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    station_id: int = Field(foreign_key="stations.id", index=True)
    charger_id: int = Field(foreign_key="chargers.id", index=True)
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicles.id")
    reservation_date: str
    reservation_time: str
    estimated_cost: float = Field(default=0.0)
    status: str = Field(default="confirmed")  # confirmed, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChargingSession(SQLModel, table=True):
    __tablename__ = "charging_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="bookings.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    battery_percent: int = Field(default=20)
    charging_progress: int = Field(default=0)
    power_output_kw: float = Field(default=60.0)
    charging_speed: str = Field(default="Fast")
    remaining_minutes: int = Field(default=30)
    current_cost: float = Field(default=0.0)
    status: str = Field(default="charging")  # charging, completed, stopped
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    booking_id: Optional[int] = Field(default=None, foreign_key="bookings.id")
    amount: float
    method: str = Field(default="credit_card")  # credit_card, promptpay, wallet
    status: str = Field(default="paid")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Favorite(SQLModel, table=True):
    __tablename__ = "favorites"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    station_id: int = Field(foreign_key="stations.id", index=True)
