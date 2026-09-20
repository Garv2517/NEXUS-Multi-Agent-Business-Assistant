import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator
from ..core.config import settings


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Returns absolute path to SQLite database, ensuring parent directories exist."""
    db_path = custom_path or settings.get_database_path()
    if db_path != ":memory:":
        path_obj = Path(db_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        return str(path_obj)
    return ":memory:"


def get_db_connection(custom_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Creates and configures a SQLite connection.
    Enables foreign keys and returns rows accessible as dictionary-like objects.
    """
    path = get_db_path(custom_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db(custom_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database transactions."""
    conn = get_db_connection(custom_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(custom_path: Optional[str] = None) -> None:
    """
    Initializes database schema and runs seed process safely.
    Idempotent: safe to run multiple times without duplicating rows.
    """
    from .schema import create_schema
    from .seed import seed_database

    with get_db(custom_path) as conn:
        create_schema(conn)
        seed_database(conn)
