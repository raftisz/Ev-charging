"""Charger management routes for station equipment."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["chargers"])


@router.get("/chargers", response_model=list[schemas.ChargerResponse])
def list_chargers(
    station_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    if station_id is not None:
        chargers = session.exec(select(models.Charger).where(models.Charger.station_id == station_id)).all()
    else:
        chargers = session.exec(select(models.Charger)).all()
    return chargers


@router.get("/chargers/{charger_id}", response_model=schemas.ChargerResponse)
def get_charger(
    charger_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    charger = crud.get_charger_by_id(session, charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger


@router.post("/chargers", response_model=schemas.ChargerResponse, status_code=201)
def create_charger(
    data: schemas.ChargerCreateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    station = crud.get_station_by_id(session, data.station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return crud.create_charger(session, data.model_dump())


@router.put("/chargers/{charger_id}", response_model=schemas.ChargerResponse)
def update_charger(
    charger_id: int,
    data: schemas.ChargerUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    charger = crud.get_charger_by_id(session, charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return crud.update_charger(session, charger, data.model_dump(exclude_unset=True))


@router.delete("/chargers/{charger_id}", status_code=204)
def remove_charger(
    charger_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    charger = crud.get_charger_by_id(session, charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    crud.delete_charger(session, charger)
    return None
