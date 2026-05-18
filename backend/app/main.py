import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import ensure_schema, wait_for_db
from .models import Base
from .routes import router


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def _parse_origins(value: str) -> list[str]:
    value = (value or "").strip()
    if not value:
        return []
    if value == "*":
        return ["*"]
    return [v.strip() for v in value.split(",") if v.strip()]


_configure_logging()
logger = logging.getLogger("app")

app = FastAPI(title="AI Receptionist Prototype API", version="0.1.0")

allow_origins = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS", "*"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Waiting for database...")
    wait_for_db()
    logger.info("Creating database tables (if missing)...")
    ensure_schema(Base)
    logger.info("Startup complete.")

