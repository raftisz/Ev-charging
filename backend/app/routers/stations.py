"""Charging station discovery and detail routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["stations"])


@router.get("/stations", response_model=list[schemas.StationResponse])
def list_stations(
    search: Optional[str] = None,
    fast_charge_only: bool = False,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_stations(session, search=search, fast_charge_only=fast_charge_only)


@router.get("/stations/{station_id}", response_model=schemas.StationDetailResponse)
def get_station(
    station_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    station = crud.get_station_by_id(session, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    chargers = crud.get_chargers_by_station(session, station_id)
    response = schemas.StationDetailResponse.model_validate(station)
    response.chargers = [schemas.ChargerResponse.model_validate(c) for c in chargers]
    return response
