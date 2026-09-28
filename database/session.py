"""
Database Session and Connection Factory.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DB_URL = os.getenv("DATABASE_URL", "sqlite:///database/banking_system_demo.db")
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
