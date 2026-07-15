from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.pool import QueuePool, StaticPool
import sys
import os

# Add parent directory to path to import core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def _build_engine(database_url: str):
    url = make_url(database_url)
    backend = url.get_backend_name()

    # SQLite benefits from a static pool in local/dev environments.
    if backend.startswith("sqlite"):
        return create_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
    )


# Create database engine with SQLite fallback for development
try:
    engine = _build_engine(settings.DATABASE_URL)
except Exception as e:
    print(f"Warning: Could not connect to PostgreSQL. Error: {e}")
    # Fallback to SQLite for testing
    engine = _build_engine("sqlite:///./test.db")
    print("Using SQLite for development/testing")


def get_engine():
    return engine
