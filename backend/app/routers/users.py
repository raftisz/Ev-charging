"""Profile and vehicle routes. All endpoints require a valid JWT."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/profile", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserResponse)
def update_profile(
    data: schemas.UserUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.update_user(session, current_user, data.model_dump(exclude_unset=True))


@router.get("/vehicles", response_model=list[schemas.VehicleResponse])
def list_vehicles(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.get_vehicles_by_user(session, current_user.id)


@router.post("/vehicles", response_model=schemas.VehicleResponse, status_code=201)
def add_vehicle(
    data: schemas.VehicleCreateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.create_vehicle(session, current_user.id, data.model_dump())


@router.get("/favorites")
def list_favorites(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    favorites = crud.get_favorites_by_user(session, current_user.id)
    return [{"station_id": f.station_id} for f in favorites]


@router.post("/favorites/{station_id}", status_code=201)
def add_favorite(
    station_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    favorite = crud.add_favorite(session, current_user.id, station_id)
    return {"station_id": favorite.station_id}
