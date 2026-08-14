"""
db.py — Database engine, session handling, and schema upkeep.

Defaults to a local SQLite file so the project runs with zero setup. Point
DATABASE_URL at Postgres (e.g. postgresql+psycopg://user:pass@host/db) to
switch backends without touching any other code.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, inspect, text
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


# Columns added after the first release. create_all() creates missing *tables*
# but never alters existing ones, so a database made before these existed would
# break on startup without this. Each entry is a full ALTER-safe definition.
_ADDED_COLUMNS: dict[str, dict[str, str]] = {
    "users": {
        "role": "VARCHAR(20) NOT NULL DEFAULT 'recruiter'",
        "company": "VARCHAR(200) DEFAULT ''",
        "cv_text": "TEXT DEFAULT ''",
        "cv_filename": "VARCHAR(255) DEFAULT ''",
    },
}


def _add_missing_columns() -> None:
    """Bring existing tables up to date with columns added in later versions."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table, columns in _ADDED_COLUMNS.items():
        if table not in existing_tables:
            continue  # create_all() will build it complete
        present = {c["name"] for c in inspector.get_columns(table)}
        for column, definition in columns.items():
            if column in present:
                continue
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            print(f"🔧 Schema updated: added {table}.{column}")


def init_db() -> None:
    """Create any missing tables, then patch in any newly added columns.
    Safe to call on every boot."""
    Base.metadata.create_all(engine)
    _add_missing_columns()


def get_session() -> Session:
    return SessionLocal()
