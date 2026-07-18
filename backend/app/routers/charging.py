"""Live charging session routes: check status, start/stop charging."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["charging"])


@router.post("/charging/start/{booking_id}", response_model=schemas.ChargingSessionResponse)
def start_charging(
    booking_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = crud.get_booking_by_id(session, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    return crud.get_or_create_active_session(session, booking, current_user.id)


@router.get("/charging/status", response_model=schemas.ChargingSessionResponse)
def charging_status(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    charging_session = crud.get_latest_session_for_user(session, current_user.id)
    if not charging_session:
        raise HTTPException(status_code=404, detail="No active or recent charging session")

    # Simulate battery progress advancing each time the status is polled,
    # since there is no real hardware connected in this university project.
    if charging_session.status == "charging" and charging_session.battery_percent < 100:
        charging_session.battery_percent = min(100, charging_session.battery_percent + 4)
        charging_session.charging_progress = charging_session.battery_percent
        charging_session.remaining_minutes = max(0, charging_session.remaining_minutes - 3)
        charging_session.current_cost = round(charging_session.current_cost + 12.5, 2)
        if charging_session.battery_percent >= 100:
            charging_session.status = "completed"
        session.add(charging_session)
        session.commit()
        session.refresh(charging_session)

    return charging_session


@router.post("/charging/stop", response_model=schemas.ChargingSessionResponse)
def stop_charging(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    charging_session = crud.get_latest_session_for_user(session, current_user.id)
    if not charging_session or charging_session.status != "charging":
        raise HTTPException(status_code=400, detail="No active charging session to stop")

    return crud.stop_charging_session(session, charging_session)
