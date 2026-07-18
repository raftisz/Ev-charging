"""
Database connection and session management.
Uses SQLModel (built on SQLAlchemy + Pydantic) with PostgreSQL.
"""

import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ev_user:ev_password@localhost:5432/ev_charging_db",
)

# `pool_pre_ping` avoids stale connections when the DB container restarts.
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def create_db_and_tables() -> None:
    """Create all tables declared in models.py if they don't already exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
