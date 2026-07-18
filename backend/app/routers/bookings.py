"""Reservation routes: reserve a charging slot, list reservation history."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["bookings"])

ESTIMATED_KWH_PER_SESSION = 40.0  # simple flat estimate used for the quoted cost


@router.post("/bookings", response_model=schemas.BookingResponse, status_code=201)
def create_booking(
    data: schemas.BookingCreateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    station = crud.get_station_by_id(session, data.station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    charger = crud.get_charger_by_id(session, data.charger_id)
    if not charger or charger.station_id != station.id:
        raise HTTPException(status_code=404, detail="Charger not found at this station")
    if not charger.is_available:
        raise HTTPException(status_code=400, detail="This charger is currently unavailable")

    estimated_cost = round(station.price_per_kwh * ESTIMATED_KWH_PER_SESSION, 2)
    booking = crud.create_booking(session, current_user.id, data.model_dump(), estimated_cost)
    return booking


@router.get("/bookings", response_model=list[schemas.BookingResponse])
def list_bookings(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.get_bookings_by_user(session, current_user.id)


@router.get("/bookings/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = crud.get_booking_by_id(session, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
