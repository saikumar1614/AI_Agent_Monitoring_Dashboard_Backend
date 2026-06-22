from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import sys
import os

# Add parent directory to path to import core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# Create database engine with SQLite fallback for development
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        poolclass=NullPool,
        future=True,
    )
except Exception as e:
    print(f"Warning: Could not connect to PostgreSQL. Error: {e}")
    # Fallback to SQLite for testing
    engine = create_engine(
        "sqlite:///./test.db",
        echo=settings.DEBUG,
        future=True,
    )
    print("Using SQLite for development/testing")


def get_engine():
    return engine
