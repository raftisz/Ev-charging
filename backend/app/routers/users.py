"""Profile and vehicle routes. All endpoints require a valid JWT."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/profile", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserResponse)
def update_profile(
    data: schemas.UserUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.update_user(session, current_user, data.model_dump(exclude_unset=True))


@router.post("/change-password", response_model=schemas.UserResponse)
def change_password(
    data: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    try:
        updated = crud.change_user_password(session, current_user, data.current_password, data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated


@router.get("/users", response_model=list[schemas.UserResponse])
def list_users(
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.get_users(session, search=search, page=page, limit=limit)


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user_profile(
    user_id: int,
    data: schemas.UserUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.update_user(session, user, data.model_dump(exclude_unset=True))


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    session.delete(user)
    session.commit()
    return None


@router.get("/check-username/{username}")
def check_username(username: str, session: Session = Depends(get_session)):
    return {"available": crud.username_is_available(session, username)}


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


@router.delete("/favorites/{favorite_id}", status_code=204)
def remove_favorite(
    favorite_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    crud.delete_favorite(session, current_user.id, favorite_id)
    return None
