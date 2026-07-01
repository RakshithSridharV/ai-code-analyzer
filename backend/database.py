"""
database.py
───────────
SQLAlchemy Core (no ORM) persistence layer.

Tables
──────
  users
    id             INTEGER  PRIMARY KEY AUTOINCREMENT
    email          TEXT     UNIQUE NOT NULL
    username       TEXT     UNIQUE NOT NULL
    password_hash  TEXT     NOT NULL
    created_at     TEXT     ISO-8601 UTC

  analyses
    id               INTEGER  PRIMARY KEY AUTOINCREMENT
    user_id          INTEGER  FK → users.id  (NULL = anonymous)
    timestamp        TEXT     ISO-8601 UTC
    language         TEXT
    time_complexity  TEXT
    space_complexity TEXT
    quality_score    INTEGER
    eco_score        REAL     nullable
    code_hash        TEXT     SHA-256 hex digest
    cyclomatic_score INTEGER  nullable
    halstead_bugs    REAL     nullable

SQLite file: backend/analyzer.db
"""

import hashlib
import os
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    insert,
    select,
)

# ── Database location ──────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "analyzer.db")
DB_URL  = f"sqlite:///{DB_PATH}"

# ── Engine & metadata ──────────────────────────────────────────────────────────
_engine   = create_engine(DB_URL, connect_args={"check_same_thread": False})
_metadata = MetaData()

# ── Table definitions ──────────────────────────────────────────────────────────
users = Table(
    "users",
    _metadata,
    Column("id",            Integer, primary_key=True, autoincrement=True),
    Column("email",         Text,    nullable=False, unique=True),
    Column("username",      Text,    nullable=False, unique=True),
    Column("password_hash", Text,    nullable=False),
    Column("created_at",    Text,    nullable=False),
)

analyses = Table(
    "analyses",
    _metadata,
    Column("id",               Integer, primary_key=True, autoincrement=True),
    Column("user_id",          Integer, ForeignKey("users.id"), nullable=True),
    Column("timestamp",        Text,    nullable=False),
    Column("language",         Text,    nullable=False),
    Column("time_complexity",  Text,    nullable=False),
    Column("space_complexity", Text,    nullable=False),
    Column("quality_score",    Integer, nullable=False),
    Column("eco_score",        Float,   nullable=True),
    Column("code_hash",        Text,    nullable=False),
    Column("cyclomatic_score", Integer, nullable=True),
    Column("halstead_bugs",    Float,   nullable=True),
)


# ── Public API ─────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they do not already exist, and migrate existing DBs."""
    _metadata.create_all(_engine)
    # Safe migrations for existing databases — ignored if the column already exists
    with _engine.begin() as conn:
        for ddl in (
            "ALTER TABLE analyses ADD COLUMN cyclomatic_score INTEGER",
            "ALTER TABLE analyses ADD COLUMN halstead_bugs    REAL",
        ):
            try:
                conn.execute(__import__("sqlalchemy").text(ddl))
            except Exception:
                pass  # Column already exists — ignore


# ── Code hash helper ───────────────────────────────────────────────────────────

def code_hash(source: str) -> str:
    """Return the SHA-256 hex digest of *source*."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


# ── User helpers ───────────────────────────────────────────────────────────────

def save_user(email: str, username: str, password_hash: str) -> int:
    """Insert a new user and return the new row id."""
    row = {
        "email":         email.lower().strip(),
        "username":      username.strip(),
        "password_hash": password_hash,
        "created_at":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with _engine.begin() as conn:
        result = conn.execute(insert(users).values(**row))
        return result.inserted_primary_key[0]


def get_user_by_email(email: str) -> dict | None:
    """Return a user row dict or None if not found."""
    stmt = select(users).where(users.c.email == email.lower().strip())
    with _engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    """Return a user row dict or None if not found."""
    stmt = select(users).where(users.c.id == user_id)
    with _engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    return dict(row) if row else None


# ── Analysis helpers ───────────────────────────────────────────────────────────

def save_analysis(data: dict) -> None:
    """
    Persist one analysis record.

    Keys in *data*:
      language         str
      time_complexity  str
      space_complexity str
      quality_score    int
      eco_score        float | None
      code_hash        str
      user_id          int | None   (optional)
      cyclomatic_score int | None   (optional)
      halstead_bugs    float | None (optional)
    """
    row = {
        "user_id":          data.get("user_id"),
        "timestamp":        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "language":         data["language"],
        "time_complexity":  data["time_complexity"],
        "space_complexity": data["space_complexity"],
        "quality_score":    int(data["quality_score"]),
        "eco_score":        data.get("eco_score"),
        "code_hash":        data["code_hash"],
        "cyclomatic_score": data.get("cyclomatic_score"),
        "halstead_bugs":    data.get("halstead_bugs"),
    }
    with _engine.begin() as conn:
        conn.execute(insert(analyses).values(**row))


def get_history(limit: int = 20, user_id: int | None = None) -> list[dict]:
    """
    Return the *limit* most recent analysis records for *user_id*, newest first.
    If user_id is None, returns nothing (history is per-user only).
    """
    if user_id is None:
        return []
    stmt = (
        select(analyses)
        .where(analyses.c.user_id == user_id)
        .order_by(analyses.c.timestamp.desc())
        .limit(limit)
    )
    with _engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]
