import logging

import uuid

from datetime import datetime, timezone

from typing import List



from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import Session



from .chat_rules import build_reply, is_booking_ready_for_confirmation

from .database import get_db

from .email_service import (
    get_email_config,
    is_email_enabled,
    send_booking_confirmation,
    send_staff_booking_notification,
    send_test_email,
)

from .extraction_service import resolve_extraction, session_request_type_from_rows

from .field_extraction import ExtractedFields, fields_from_booking_request, merge_fields

from .llm_service import generate_chat_reply, get_llm_config

from .models import BookingRequest, ChatSession

from .schemas import (

    BookingRequestCreate,

    BookingRequestOut,

    ChatHistoryMessage,

    ChatHistoryResponse,

    ChatRequest,

    ChatResponse,

    EmailTestResponse,

    SessionOut,

    SessionStartRequest,

    SessionStartResponse,

)



logger = logging.getLogger("app.routes")



router = APIRouter()





def _session_rows(db: Session, session_id: str) -> list[BookingRequest]:

    return (

        db.query(BookingRequest)

        .filter(BookingRequest.session_id == session_id)

        .order_by(BookingRequest.created_at.asc(), BookingRequest.id.asc())

        .all()

    )





def _get_chat_session(db: Session, session_id: str) -> ChatSession | None:

    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()





def _require_session_email(db: Session, session_id: str) -> str:

    """Return the guest email for a started session or raise 400."""

    chat_session = _get_chat_session(db, session_id)

    if chat_session is None or not chat_session.guest_email:

        raise HTTPException(

            status_code=400,

            detail="Please provide your email before starting the chat.",

        )

    return chat_session.guest_email





def _session_fields(db: Session, session_id: str, session_email: str | None = None) -> ExtractedFields:

    """Merge structured fields saved earlier in the same chat session."""

    merged = ExtractedFields()

    if session_email:

        merged = merge_fields(merged, ExtractedFields(guest_email=session_email))

    for row in _session_rows(db, session_id):

        merged = merge_fields(merged, fields_from_booking_request(row))

    return merged





def _rows_to_chat_history(rows: list[BookingRequest]) -> list[dict[str, str]]:

    history: list[dict[str, str]] = []

    for row in rows:

        if row.raw_message:

            history.append({"role": "user", "content": row.raw_message})

        if row.ai_reply:

            history.append({"role": "assistant", "content": row.ai_reply})

    return history





def _rows_to_history_messages(rows: list[BookingRequest]) -> list[ChatHistoryMessage]:

    messages: list[ChatHistoryMessage] = []

    for row in rows:

        if row.raw_message:

            messages.append(

                ChatHistoryMessage(

                    id=f"user-{row.id}",

                    role="user",

                    text=row.raw_message,

                    created_at=row.created_at,

                )

            )

        if row.ai_reply:

            messages.append(

                ChatHistoryMessage(

                    id=f"assistant-{row.id}",

                    role="assistant",

                    text=row.ai_reply,

                    created_at=row.created_at,

                )

            )

    return messages





@router.post("/api/session/start", response_model=SessionStartResponse)

def start_session(payload: SessionStartRequest, db: Session = Depends(get_db)):

    """Create or update a chat session with the guest email before chat begins."""

    session_id = (payload.session_id or str(uuid.uuid4())).strip()

    guest_email = payload.email



    try:

        chat_session = _get_chat_session(db, session_id)

        if chat_session is None:

            chat_session = ChatSession(session_id=session_id, guest_email=guest_email)

            db.add(chat_session)

        else:

            chat_session.guest_email = guest_email

        db.commit()

        db.refresh(chat_session)

        logger.info("Session started session_id=%s", session_id)

        return SessionStartResponse(session_id=session_id, guest_email=chat_session.guest_email)

    except SQLAlchemyError as e:

        db.rollback()

        logger.exception("Failed to start session")

        raise HTTPException(status_code=500, detail="Database write failed") from e





@router.get("/api/session/{session_id}", response_model=SessionOut)

def get_session(session_id: str, db: Session = Depends(get_db)):

    session_id = session_id.strip()

    if not session_id:

        raise HTTPException(status_code=400, detail="session_id is required")



    chat_session = _get_chat_session(db, session_id)

    if chat_session is None:

        raise HTTPException(status_code=404, detail="Session not found")

    return chat_session





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





@router.get("/api/chat-history/{session_id}", response_model=ChatHistoryResponse)

def get_chat_history(session_id: str, db: Session = Depends(get_db)):

    session_id = session_id.strip()

    if not session_id:

        raise HTTPException(status_code=400, detail="session_id is required")



    chat_session = _get_chat_session(db, session_id)

    rows = _session_rows(db, session_id)

    return ChatHistoryResponse(

        session_id=session_id,

        guest_email=chat_session.guest_email if chat_session else None,

        messages=_rows_to_history_messages(rows),

    )





@router.post("/api/chat", response_model=ChatResponse)

def chat(payload: ChatRequest, db: Session = Depends(get_db)):

    if not payload.session_id:

        raise HTTPException(

            status_code=400,

            detail="session_id is required. Start a session with your email first.",

        )



    session_id = payload.session_id.strip()

    session_email = _require_session_email(db, session_id)

    prior_rows = _session_rows(db, session_id)

    session_fields = _session_fields(db, session_id, session_email=session_email)

    session_request_type = session_request_type_from_rows(prior_rows)

    chat_history = _rows_to_chat_history(prior_rows)



    merged_fields, request_type, extraction_source = resolve_extraction(

        payload.message,

        chat_history,

        session_fields,

        session_request_type,

    )

    if not merged_fields.guest_email:

        merged_fields = merge_fields(merged_fields, ExtractedFields(guest_email=session_email))

    chat_session = _get_chat_session(db, session_id)
    email_recipient = merged_fields.guest_email or session_email
    email_sent = False
    booking_ready = is_booking_ready_for_confirmation(merged_fields, request_type)
    if (
        chat_session is not None
        and chat_session.confirmation_email_sent_at is None
        and booking_ready
        and is_email_enabled()
    ):
        if send_booking_confirmation(
            email_recipient,
            merged_fields,
            request_type=request_type,
        ):
            send_staff_booking_notification(
                merged_fields,
                guest_email=email_recipient,
                request_type=request_type,
            )
            chat_session.confirmation_email_sent_at = datetime.now(timezone.utc)
            email_sent = True
        else:
            logger.error(
                "Booking complete but confirmation email failed for session_id=%s recipient=%s",
                session_id,
                email_recipient,
            )
    elif booking_ready and not is_email_enabled():
        logger.warning(
            "Booking complete but email not sent (SMTP not configured) session_id=%s recipient=%s",
            session_id,
            email_recipient,
        )

    fallback_reply = build_reply(
        request_type,
        merged_fields,
        email_sent=email_sent,
        email_recipient=email_recipient if email_sent else None,
        booking_ready=booking_ready,
    )

    reply = generate_chat_reply(

        payload.message,

        chat_history,

        merged_fields,

        request_type=request_type,

        fallback_reply=fallback_reply,

        email_sent=email_sent,

        email_recipient=email_recipient if email_sent else None,

        booking_ready=booking_ready,

    )

    logger.info(

        "Chat reply generated session_id=%s request_type=%s source=%s llm_enabled=%s",

        session_id,

        request_type,

        extraction_source,

        get_llm_config()["enabled"],

    )



    try:

        req = BookingRequest(

            session_id=session_id,

            raw_message=payload.message,

            guest_name=merged_fields.guest_name,

            guest_email=merged_fields.guest_email or session_email,

            guest_phone=merged_fields.guest_phone,

            check_in=merged_fields.check_in,

            check_out=merged_fields.check_out,

            guests_count=merged_fields.guests_count,

            request_type=request_type,

            special_request=merged_fields.special_request,

            ai_reply=reply,

        )

        db.add(req)

        db.commit()

        logger.info(

            "Chat message saved session_id=%s request_type=%s merged_fields=%s",

            session_id,

            request_type,

            merged_fields,

        )

        return ChatResponse(reply=reply, session_id=session_id)

    except SQLAlchemyError as e:

        db.rollback()

        logger.exception("Failed to persist chat message")

        raise HTTPException(status_code=500, detail="Database write failed") from e





@router.get("/health")

def health():

    llm = get_llm_config()
    email = get_email_config()

    return {

        "status": "ok",

        "llm": {

            "enabled": llm["enabled"],

            "configured": llm["configured"],

            "active": llm["active"],

            "reply_mode": llm["reply_mode"],

            "provider": llm["provider"],

            "model": llm["model"],

            "chat_temperature": llm["chat_temperature"],

            "chat_max_tokens": llm["chat_max_tokens"],

        },

        "email": {

            "enabled": email["enabled"],

            "configured": email["configured"],

            "provider": email["provider"],

            "smtp_host": email["smtp_host"],

            "mailpit_mode": email["mailpit_mode"],

            "mailpit_ui": email["mailpit_ui"] if email["mailpit_mode"] else None,

            "resend_configured": email["resend_configured"],

            "notify_email_set": bool(email.get("notify_email")),

        },

    }


@router.post("/api/email/test", response_model=EmailTestResponse)
def test_email():
    """Send a test booking email to BOOKING_NOTIFY_EMAIL or SMTP_USER."""
    cfg = get_email_config()
    recipient = str(cfg.get("notify_email") or cfg.get("smtp_user") or "").strip()
    if not recipient:
        raise HTTPException(
            status_code=400,
            detail="Set BOOKING_NOTIFY_EMAIL or SMTP_USER in .env first.",
        )
    if not is_email_enabled():
        raise HTTPException(
            status_code=503,
            detail="Email is not configured. Set Mailpit SMTP or RESEND_API_KEY in .env.",
        )

    ok = send_test_email(recipient)
    provider = str(cfg["provider"])
    mailpit_ui = str(cfg["mailpit_ui"]) if cfg["mailpit_mode"] else None
    if ok and cfg["mailpit_mode"]:
        message = f"Test email captured by Mailpit for {recipient}. Open {mailpit_ui} to view it."
    elif ok:
        message = f"Test email sent to {recipient}."
    else:
        message = f"Failed to send test email to {recipient}. Check backend logs."

    return EmailTestResponse(
        ok=ok,
        message=message,
        provider=provider,
        mailpit_ui=mailpit_ui,
    )
