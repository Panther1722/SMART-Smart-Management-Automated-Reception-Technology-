from datetime import datetime

from pydantic import BaseModel, Field


class BookingRequestCreate(BaseModel):
    message: str = Field(
        default="Booking request submitted from prototype",
        max_length=500,
    )


class BookingRequestOut(BaseModel):
    id: int
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}

