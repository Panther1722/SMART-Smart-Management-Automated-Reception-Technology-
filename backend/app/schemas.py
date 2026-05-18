from datetime import date, datetime

from pydantic import BaseModel, Field


class BookingRequestCreate(BaseModel):
    session_id: str | None = Field(default=None, max_length=100)
    raw_message: str | None = Field(default=None, max_length=2000)
    guest_name: str | None = Field(default=None, max_length=200)
    guest_email: str | None = Field(default=None, max_length=320)
    guest_phone: str | None = Field(default=None, max_length=50)
    check_in: date | None = None
    check_out: date | None = None
    guests_count: int | None = Field(default=None, ge=1)
    request_type: str | None = Field(default=None, max_length=50)
    special_request: str | None = None
    ai_reply: str | None = None


class BookingRequestOut(BaseModel):
    id: int
    session_id: str | None
    raw_message: str | None
    guest_name: str | None
    guest_email: str | None
    guest_phone: str | None
    check_in: date | None
    check_out: date | None
    guests_count: int | None
    request_type: str | None
    special_request: str | None
    ai_reply: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    reply: str
    session_id: str
