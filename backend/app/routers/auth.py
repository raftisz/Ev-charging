"""Authentication routes: register and login. These are the only public endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session

router = APIRouter(prefix="/api", tags=["auth"])

# Points at /api/login purely so Swagger UI's "Authorize" button works.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> models.User:
    """Shared dependency used by every protected router to enforce JWT auth."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error

    user_id = crud.decode_access_token(token)
    if user_id is None:
        raise credentials_error

    user = crud.get_user_by_id(session, user_id)
    if user is None:
        raise credentials_error

    return user



@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: schemas.RegisterRequest, session: Session = Depends(get_session)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if crud.get_user_by_email(session, data.email):
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = crud.create_user(session, data.full_name, data.email, data.phone, data.password)
    token = crud.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token, user_id=user.id, full_name=user.full_name)


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, session: Session = Depends(get_session)):
    user = crud.get_user_by_email(session, data.email)
    if not user or not crud.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = crud.create_access_token(user.id, remember_me=data.remember_me)
    return schemas.TokenResponse(access_token=token, user_id=user.id, full_name=user.full_name)
