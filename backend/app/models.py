from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    raw_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    guest_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    check_in: Mapped[date | None] = mapped_column(Date, nullable=True)
    check_out: Mapped[date | None] = mapped_column(Date, nullable=True)
    guests_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    special_request: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
