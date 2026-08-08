"""Payment routes: pay for a charging session, list payment history."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["payments"])


@router.post("/payments", response_model=schemas.PaymentResponse, status_code=201)
def create_payment(
    data: schemas.PaymentCreateRequest,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if data.method == "wallet" and current_user.wallet_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    return crud.create_payment(session, current_user.id, data.model_dump())


@router.get("/payments", response_model=list[schemas.PaymentResponse])
def list_payments(
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return crud.get_payments_by_user(session, current_user.id)


@router.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    payment = crud.get_payment_by_id(session, payment_id)
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
