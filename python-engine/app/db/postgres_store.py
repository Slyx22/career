"""
Postgres storage backend (direct database connection).

Used when DATABASE_URL is set, e.g. a Supabase Postgres connection string
for a dedicated low-privilege database role that can only read and insert
into engine_analyses / engine_certificates. This keeps analyses and
certificates permanently, unlike the SQLite file, which Render's free plan
wipes on every restart.

Tables: supabase/migrations/0006_engine_storage.sql.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from app.db.interface import Repository

_CERT_COLS = "certificate_id, analysis_id, first_name, surname, career, score, clerk_user_id, issued_at"
_ANALYSIS_COLS = "id, first_name, surname, career, score, payload, clerk_user_id, created_at"


def _iso(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


class PostgresStore(Repository):
    def __init__(self, dsn: str, connect_timeout: int = 15):
        self.dsn = dsn
        self.connect_timeout = connect_timeout

    def _connect(self):
        # One short connection per request: simple and safe with Supabase's
        # connection pooler; prepare_threshold=None keeps it compatible with
        # transaction-mode pooling too.
        return psycopg.connect(
            self.dsn,
            connect_timeout=self.connect_timeout,
            row_factory=dict_row,
            prepare_threshold=None,
        )

    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        with self._connect() as conn:
            conn.execute(
                f"insert into engine_analyses ({_ANALYSIS_COLS}) values (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)",
                (
                    analysis["id"], analysis["first_name"], analysis["surname"], analysis["career"],
                    analysis["score"], json.dumps(analysis["payload"]), analysis.get("clerk_user_id"),
                    analysis["created_at"],
                ),
            )
        return analysis["id"]

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(f"select {_ANALYSIS_COLS} from engine_analyses where id = %s", (analysis_id,)).fetchone()
        if not row:
            return None
        row["created_at"] = _iso(row["created_at"])
        if isinstance(row["payload"], str):
            row["payload"] = json.loads(row["payload"])
        return row

    def save_certificate(self, certificate: Dict[str, Any]) -> str:
        with self._connect() as conn:
            conn.execute(
                f"insert into engine_certificates ({_CERT_COLS}) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    certificate["certificate_id"], certificate["analysis_id"], certificate["first_name"],
                    certificate["surname"], certificate["career"], certificate["score"],
                    certificate.get("clerk_user_id"), certificate["issued_at"],
                ),
            )
        return certificate["certificate_id"]

    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                f"select {_CERT_COLS} from engine_certificates where certificate_id = %s", (certificate_id,)
            ).fetchone()
        if row:
            row["issued_at"] = _iso(row["issued_at"])
        return row

    def list_certificates_for_user(self, clerk_user_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                f"select {_CERT_COLS} from engine_certificates where clerk_user_id = %s order by issued_at desc",
                (clerk_user_id,),
            ).fetchall()
        for r in rows:
            r["issued_at"] = _iso(r["issued_at"])
        return rows
