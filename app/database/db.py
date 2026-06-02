from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path

from app.database.models import Base
from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("database")

# Ensure the data directory exists
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{settings.DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialised → {settings.DB_PATH}")


@contextmanager
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
