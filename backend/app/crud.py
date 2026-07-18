"""
CRUD operations and authentication helpers (password hashing + JWT).
Kept in one module per the required project structure.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app import models

# ---------- Auth config ----------

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
REMEMBER_ME_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: int, remember_me: bool = False) -> str:
    minutes = REMEMBER_ME_EXPIRE_MINUTES if remember_me else ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id is not None else None
    except JWTError:
        return None


# ---------- Users ----------

def get_user_by_email(session: Session, email: str) -> Optional[models.User]:
    return session.exec(select(models.User).where(models.User.email == email)).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[models.User]:
    return session.get(models.User, user_id)


def create_user(session: Session, full_name: str, email: str, phone: Optional[str], password: str) -> models.User:
    user = models.User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: models.User, data: dict) -> models.User:
    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ---------- Vehicles ----------

def get_vehicles_by_user(session: Session, user_id: int):
    return session.exec(select(models.Vehicle).where(models.Vehicle.user_id == user_id)).all()


def create_vehicle(session: Session, user_id: int, data: dict) -> models.Vehicle:
    vehicle = models.Vehicle(user_id=user_id, **data)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


# ---------- Stations ----------

def get_stations(session: Session, search: Optional[str] = None, fast_charge_only: bool = False):
    query = select(models.Station)
    if search:
        query = query.where(models.Station.name.ilike(f"%{search}%"))
    if fast_charge_only:
        query = query.where(models.Station.has_fast_charge == True)  # noqa: E712
    return session.exec(query).all()


def get_station_by_id(session: Session, station_id: int) -> Optional[models.Station]:
    return session.get(models.Station, station_id)


def get_chargers_by_station(session: Session, station_id: int):
    return session.exec(select(models.Charger).where(models.Charger.station_id == station_id)).all()


def get_charger_by_id(session: Session, charger_id: int) -> Optional[models.Charger]:
    return session.get(models.Charger, charger_id)


# ---------- Bookings ----------

def create_booking(session: Session, user_id: int, data: dict, estimated_cost: float) -> models.Booking:
    booking = models.Booking(user_id=user_id, estimated_cost=estimated_cost, **data)
    session.add(booking)
    session.commit()
    session.refresh(booking)

    # Mark the charger as occupied and start a charging session automatically
    charger = session.get(models.Charger, data["charger_id"])
    if charger:
        charger.is_available = False
        session.add(charger)

    session.commit()
    return booking


def get_bookings_by_user(session: Session, user_id: int):
    return session.exec(
        select(models.Booking).where(models.Booking.user_id == user_id).order_by(models.Booking.created_at.desc())
    ).all()


def get_booking_by_id(session: Session, booking_id: int) -> Optional[models.Booking]:
    return session.get(models.Booking, booking_id)


# ---------- Charging Sessions ----------

def get_or_create_active_session(session: Session, booking: models.Booking, user_id: int) -> models.ChargingSession:
    existing = session.exec(
        select(models.ChargingSession)
        .where(models.ChargingSession.booking_id == booking.id)
        .where(models.ChargingSession.status == "charging")
    ).first()
    if existing:
        return existing

    charging_session = models.ChargingSession(
        booking_id=booking.id,
        user_id=user_id,
        battery_percent=20,
        charging_progress=0,
        power_output_kw=60.0,
        charging_speed="Fast",
        remaining_minutes=35,
        current_cost=0.0,
        status="charging",
    )
    session.add(charging_session)
    session.commit()
    session.refresh(charging_session)
    return charging_session


def get_latest_session_for_user(session: Session, user_id: int) -> Optional[models.ChargingSession]:
    return session.exec(
        select(models.ChargingSession)
        .where(models.ChargingSession.user_id == user_id)
        .order_by(models.ChargingSession.started_at.desc())
    ).first()


def stop_charging_session(session: Session, charging_session: models.ChargingSession) -> models.ChargingSession:
    charging_session.status = "stopped"
    charging_session.ended_at = datetime.utcnow()
    session.add(charging_session)

    booking = session.get(models.Booking, charging_session.booking_id)
    if booking:
        booking.status = "completed"
        session.add(booking)
        charger = session.get(models.Charger, booking.charger_id)
        if charger:
            charger.is_available = True
            session.add(charger)

    session.commit()
    session.refresh(charging_session)
    return charging_session


# ---------- Payments ----------

def create_payment(session: Session, user_id: int, data: dict) -> models.Payment:
    payment = models.Payment(user_id=user_id, **data)
    session.add(payment)

    user = session.get(models.User, user_id)
    if user:
        if data["method"] == "wallet":
            user.wallet_balance = max(0.0, user.wallet_balance - data["amount"])
        user.reward_points += int(data["amount"] // 10)
        session.add(user)

    session.commit()
    session.refresh(payment)
    return payment


def get_payments_by_user(session: Session, user_id: int):
    return session.exec(
        select(models.Payment).where(models.Payment.user_id == user_id).order_by(models.Payment.created_at.desc())
    ).all()


# ---------- Favorites ----------

def get_favorites_by_user(session: Session, user_id: int):
    return session.exec(select(models.Favorite).where(models.Favorite.user_id == user_id)).all()


def add_favorite(session: Session, user_id: int, station_id: int) -> models.Favorite:
    favorite = models.Favorite(user_id=user_id, station_id=station_id)
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite
