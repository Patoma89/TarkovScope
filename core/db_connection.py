"""TarkovScope - Conexion SQLite optimizada (WAL, rollback automatico).
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Set
from core.config import DB_PATH

_WAL_INITIALIZED_PATHS: Set[str] = set()


@contextmanager
def get_db_connection(db_path: str = DB_PATH) -> Iterator[sqlite3.Connection]:
    """Retorna una conexión a SQLite optimizada para alto rendimiento y la cierra al salir del bloque."""
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    norm_path = os.path.abspath(db_path)
    if norm_path not in _WAL_INITIALIZED_PATHS:
        conn.execute("PRAGMA journal_mode = WAL;")
        _WAL_INITIALIZED_PATHS.add(norm_path)
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
