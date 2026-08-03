"""
db.py — Database engine and session handling.

Defaults to a local SQLite file so the project runs with zero setup. Point
DATABASE_URL at Postgres (e.g. postgresql+psycopg://user:pass@host/db) to
switch backends without touching any other code.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from models import Base

# Read at import time, which runs before app.py's load_dotenv() — so load here too.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///recruitment.db")

# check_same_thread=False is required because Flask serves requests on
# multiple threads while SQLite defaults to single-thread ownership.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)

if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        """SQLite ignores FK constraints (and our ON DELETE rules) unless asked."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


def init_db() -> None:
    """Create any missing tables. Safe to call on every boot."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()
