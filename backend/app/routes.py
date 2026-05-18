import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .chat_rules import build_reply, detect_request_type
from .database import get_db
from .models import BookingRequest
from .schemas import BookingRequestCreate, BookingRequestOut, ChatRequest, ChatResponse

logger = logging.getLogger("app.routes")

router = APIRouter()


@router.post("/api/booking-request", response_model=BookingRequestOut)
def create_booking_request(payload: BookingRequestCreate, db: Session = Depends(get_db)):
    try:
        req = BookingRequest(**payload.model_dump())
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


@router.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session_id = payload.session_id or str(uuid.uuid4())
    request_type = detect_request_type(payload.message)
    reply = build_reply(payload.message, request_type)

    try:
        req = BookingRequest(
            session_id=session_id,
            raw_message=payload.message,
            request_type=request_type,
            ai_reply=reply,
        )
        db.add(req)
        db.commit()
        logger.info("Chat message saved session_id=%s request_type=%s", session_id, request_type)
        return ChatResponse(reply=reply, session_id=session_id)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Failed to persist chat message")
        raise HTTPException(status_code=500, detail="Database write failed") from e


@router.get("/health")
def health():
    return {"status": "ok"}
