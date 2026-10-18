"""
Database Session and Connection Factory.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

def get_normalized_database_url(url: str = None) -> str:
    """Normalizes database connection URL across PostgreSQL drivers and SQLite."""
    if not url:
        url = os.getenv("DATABASE_URL", "sqlite:///database/banking_system_demo.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        # Explicitly declare driver based on environment availability to prevent driver resolution failures
        try:
            import psycopg
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        except ImportError:
            try:
                import psycopg2
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            except ImportError:
                pass
    return url


DB_URL = get_normalized_database_url()
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
