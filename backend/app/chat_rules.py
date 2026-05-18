"""Simple rule-based chat classification and replies (no LLM)."""

from __future__ import annotations

REQUEST_TYPE_BOOKING = "booking"
REQUEST_TYPE_CANCELLATION = "cancellation"
REQUEST_TYPE_PRICING = "pricing"
REQUEST_TYPE_AVAILABILITY = "availability"
REQUEST_TYPE_GENERAL = "general inquiry"

# Order matters: check more specific intents before broader ones (e.g. booking vs availability).
_REQUEST_TYPE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        REQUEST_TYPE_CANCELLATION,
        (
            "cancel",
            "cancellation",
            "cancelled",
            "canceled",
            "refund",
            "call off",
        ),
    ),
    (
        REQUEST_TYPE_AVAILABILITY,
        (
            "availability",
            "available",
            "vacancy",
            "vacancies",
            "any rooms",
            "room available",
            "fully booked",
            "sold out",
        ),
    ),
    (
        REQUEST_TYPE_PRICING,
        (
            "price",
            "pricing",
            "cost",
            "rate",
            "rates",
            "how much",
            "per night",
            "nightly rate",
            "quote",
        ),
    ),
    (
        REQUEST_TYPE_BOOKING,
        (
            "book",
            "booking",
            "reserve",
            "reservation",
            "make a reservation",
            "check in",
            "check-in",
            "check out",
            "check-out",
            "stay",
            "room for",
        ),
    ),
)

_REPLIES: dict[str, str] = {
    REQUEST_TYPE_BOOKING: (
        "I'd be happy to help you with a booking. "
        "Could you share your preferred check-in and check-out dates, "
        "how many guests will be staying, and your name?"
    ),
    REQUEST_TYPE_CANCELLATION: (
        "I can help with a cancellation. "
        "Please share the name on the reservation and your check-in date "
        "(or booking reference if you have one), and I'll guide you through the next steps."
    ),
    REQUEST_TYPE_PRICING: (
        "I can share our current rates. "
        "Which dates are you interested in, and how many guests will you have? "
        "That way I can point you to the right options."
    ),
    REQUEST_TYPE_AVAILABILITY: (
        "I'll check availability for you. "
        "What check-in and check-out dates are you looking at, and how many guests?"
    ),
    REQUEST_TYPE_GENERAL: (
        "Thank you for reaching out. I'm here to help with bookings, availability, "
        "pricing, and cancellations. What would you like to know?"
    ),
}


def detect_request_type(message: str) -> str:
    """Classify the guest message using simple keyword matching."""
    normalized = " ".join(message.lower().split())
    if not normalized:
        return REQUEST_TYPE_GENERAL

    for request_type, keywords in _REQUEST_TYPE_RULES:
        if any(keyword in normalized for keyword in keywords):
            return request_type

    return REQUEST_TYPE_GENERAL


def build_reply(message: str, request_type: str) -> str:
    """Return a friendly receptionist-style reply for the detected request type."""
    _ = message  # reserved for future rule-based personalization
    return _REPLIES.get(request_type, _REPLIES[REQUEST_TYPE_GENERAL])
