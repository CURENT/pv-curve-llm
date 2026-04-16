from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from web.backend.core.config import get_settings
import os


class Base(DeclarativeBase):
    pass


def _get_engine():
    settings = get_settings()
    db_path = settings.database_path

    # Create parent directories if needed (e.g. /data/web_app.db)
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    # Enable WAL mode so multiple readers can work alongside one writer
    @event.listens_for(engine, "connect")
    def set_wal_mode(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return engine


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables. Call once at application startup."""
    from web.backend.database import models  # noqa: F401 - registers models
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
