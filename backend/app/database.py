import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_attempts: int = 30, sleep_seconds: float = 1.0) -> None:
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:  # noqa: BLE001 - startup retry loop
            last_err = e
            time.sleep(sleep_seconds)
    raise RuntimeError(f"Database not reachable after {max_attempts} attempts") from last_err

