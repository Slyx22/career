"""
Local development storage backend (SQLite).

This exists so the whole application runs locally with zero external
services, per build spec section 3 ("do not require an actual Supabase
project during development"). The schema mirrors supabase/migrations so
moving to Supabase later is a matter of writing a SupabaseStore that
implements the same Repository interface.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from typing import Any, Dict, Optional

from app.db.interface import Repository

DB_PATH = os.environ.get("LOCAL_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "local_dev.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    career TEXT NOT NULL,
    score INTEGER NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certificates (
    certificate_id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    career TEXT NOT NULL,
    score INTEGER NOT NULL,
    issued_at TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
"""


class LocalStore(Repository):
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO analyses (id, first_name, surname, career, score, payload, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    analysis["id"],
                    analysis["first_name"],
                    analysis["surname"],
                    analysis["career"],
                    analysis["score"],
                    json.dumps(analysis["payload"]),
                    analysis["created_at"],
                ),
            )
        return analysis["id"]

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, first_name, surname, career, score, payload, created_at FROM analyses WHERE id = ?",
                (analysis_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "first_name": row[1],
            "surname": row[2],
            "career": row[3],
            "score": row[4],
            "payload": json.loads(row[5]),
            "created_at": row[6],
        }

    def save_certificate(self, certificate: Dict[str, Any]) -> str:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO certificates (certificate_id, analysis_id, first_name, surname, career, score, issued_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    certificate["certificate_id"],
                    certificate["analysis_id"],
                    certificate["first_name"],
                    certificate["surname"],
                    certificate["career"],
                    certificate["score"],
                    certificate["issued_at"],
                ),
            )
        return certificate["certificate_id"]

    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT certificate_id, analysis_id, first_name, surname, career, score, issued_at "
                "FROM certificates WHERE certificate_id = ?",
                (certificate_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "certificate_id": row[0],
            "analysis_id": row[1],
            "first_name": row[2],
            "surname": row[3],
            "career": row[4],
            "score": row[5],
            "issued_at": row[6],
        }


_store_instance: Optional[LocalStore] = None


def get_store() -> Repository:
    """
    Storage factory. Reads STORAGE_BACKEND to decide which implementation
    to use. Only 'local' (SQLite) is implemented in Phase 1; 'supabase' is
    a documented extension point for later.
    """
    global _store_instance
    backend = os.environ.get("STORAGE_BACKEND", "local")
    if backend == "supabase":
        raise NotImplementedError(
            "Supabase backend not yet implemented. Implement app/db/supabase_store.py "
            "against the Repository interface and wire it in here when you're ready to launch."
        )
    if _store_instance is None:
        _store_instance = LocalStore()
    return _store_instance
