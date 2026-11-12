"""TarkovScope - Conexion SQLite optimizada (WAL, rollback automatico).
"""
import sqlite3
from contextlib import contextmanager
from typing import Iterator
from core.config import DB_PATH


@contextmanager
def get_db_connection(db_path: str = DB_PATH) -> Iterator[sqlite3.Connection]:
    """Retorna una conexión a SQLite optimizada para alto rendimiento y la cierra al salir del bloque."""
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
