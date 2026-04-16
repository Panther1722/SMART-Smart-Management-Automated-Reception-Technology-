import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .models import BookingRequest
from .schemas import BookingRequestCreate, BookingRequestOut

logger = logging.getLogger("app.routes")

router = APIRouter()


@router.post("/api/booking-request", response_model=BookingRequestOut)
def create_booking_request(payload: BookingRequestCreate, db: Session = Depends(get_db)):
    try:
        req = BookingRequest(message=payload.message)
        db.add(req)
        db.commit()
        db.refresh(req)
        return req
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Failed to create booking request")
        raise HTTPException(status_code=500, detail="Database write failed") from e


@router.get("/api/booking-requests", response_model=List[BookingRequestOut])
def list_booking_requests(db: Session = Depends(get_db)):
    return (
        db.query(BookingRequest)
        .order_by(BookingRequest.created_at.desc(), BookingRequest.id.desc())
        .limit(100)
        .all()
    )


@router.get("/health")
def health():
    return {"status": "ok"}
