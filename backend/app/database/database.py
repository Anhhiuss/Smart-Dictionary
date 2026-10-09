"""Database configuration and session management using SQLAlchemy and SQLite."""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Path to persistent SQLite database
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "smart_dictionary.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Engine with SQLite-specific foreign keys and thread check settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables defined on Base metadata."""
    from backend.app.models.word import Word  # noqa: F401
    Base.metadata.create_all(bind=engine)
