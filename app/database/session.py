from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# The engine is the app's connection point to the database.
engine = create_engine(settings.database_url, connect_args=connect_args)

# SessionLocal creates short-lived database sessions for each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session]:
    # FastAPI runs this dependency before a route, then closes the session after.
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
