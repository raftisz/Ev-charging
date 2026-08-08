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
    city: Optional[str] = None,
    fast_charge_only: bool = False,
    available_only: bool = False,
    page: int = 1,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_stations(
        session,
        search=search,
        city=city,
        fast_charge_only=fast_charge_only,
        available_only=available_only,
        page=page,
        limit=limit,
    )


@router.get("/stations/search", response_model=list[schemas.StationResponse])
def search_stations(
    q: Optional[str] = None,
    city: Optional[str] = None,
    fast_charge_only: bool = False,
    available_only: bool = False,
    page: int = 1,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_stations(
        session,
        search=q,
        city=city,
        fast_charge_only=fast_charge_only,
        available_only=available_only,
        page=page,
        limit=limit,
    )


@router.get("/stations/popular", response_model=list[schemas.StationResponse])
def popular_stations(
    limit: int = 5,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    stations = crud.get_stations(session, page=1, limit=limit)
    return sorted(stations, key=lambda station: station.rating, reverse=True)[:limit]


@router.get("/stations/nearby", response_model=list[schemas.StationResponse])
def nearby_stations(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    stations = crud.get_stations(session, page=1, limit=100)
    if latitude is None or longitude is None:
        return stations[:limit]
    stations.sort(
        key=lambda station: (station.latitude - latitude) ** 2 + (station.longitude - longitude) ** 2
    )
    return stations[:limit]


@router.post("/stations", response_model=schemas.StationResponse, status_code=201)
def create_station(
    data: schemas.StationCreateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.create_station(session, data.model_dump())


@router.put("/stations/{station_id}", response_model=schemas.StationResponse)
def update_station(
    station_id: int,
    data: schemas.StationUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    station = crud.get_station_by_id(session, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return crud.update_station(session, station, data.model_dump(exclude_unset=True))


@router.delete("/stations/{station_id}", status_code=204)
def remove_station(
    station_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    station = crud.get_station_by_id(session, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    crud.delete_station(session, station)
    return None


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
