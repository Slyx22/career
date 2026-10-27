"""
Supabase (Postgres) storage backend, using Supabase's REST API.

Why: on Render's free plan the engine's disk is wiped whenever the service
restarts or sleeps (after 15 idle minutes), so the SQLite LocalStore loses
every analysis and certificate, and certificate verify links stop working.
Supabase's free database keeps them permanently.

Turn it on by setting, on the Python engine (Render):
    SUPABASE_URL=https://<project>.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=<the service_role / secret key>
and running supabase/migrations/0006_engine_storage.sql once in the
Supabase SQL editor. The service key stays on the server and is never
sent to browsers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from app.db.interface import Repository

ANALYSES_TABLE = "engine_analyses"
CERTIFICATES_TABLE = "engine_certificates"

_CERT_FIELDS = "certificate_id,analysis_id,first_name,surname,career,score,clerk_user_id,issued_at"
_ANALYSIS_FIELDS = "id,first_name,surname,career,score,payload,clerk_user_id,created_at"


class StorageError(Exception):
    pass


class SupabaseStore(Repository):
    def __init__(self, url: str, service_key: str, timeout: float = 15.0, session: Optional[requests.Session] = None):
        self.base = url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self.session = session or requests.Session()
        headers = {
            "apikey": service_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Legacy keys are JWTs and go in Authorization too; the newer
        # "sb_secret_..." keys must only be sent as apikey.
        if service_key.startswith("eyJ"):
            headers["Authorization"] = f"Bearer {service_key}"
        self.headers = headers

    # --- helpers -------------------------------------------------------
    def _insert(self, table: str, row: Dict[str, Any]) -> None:
        resp = self.session.post(
            f"{self.base}/{table}",
            json=row,
            headers={**self.headers, "Prefer": "return=minimal"},
            timeout=self.timeout,
        )
        if resp.status_code not in (200, 201, 204):
            raise StorageError(f"Saving to {table} failed ({resp.status_code}): {resp.text[:200]}")

    def _select(self, table: str, fields: str, filters: str, order: str = "") -> List[Dict[str, Any]]:
        url = f"{self.base}/{table}?select={fields}&{filters}"
        if order:
            url += f"&order={order}"
        resp = self.session.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise StorageError(f"Reading {table} failed ({resp.status_code}): {resp.text[:200]}")
        return resp.json()

    @staticmethod
    def _eq(value: str) -> str:
        return "eq." + quote(str(value), safe="")

    # --- Repository ----------------------------------------------------
    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        self._insert(ANALYSES_TABLE, {
            "id": analysis["id"],
            "first_name": analysis["first_name"],
            "surname": analysis["surname"],
            "career": analysis["career"],
            "score": analysis["score"],
            "payload": analysis["payload"],
            "clerk_user_id": analysis.get("clerk_user_id"),
            "created_at": analysis["created_at"],
        })
        return analysis["id"]

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        rows = self._select(ANALYSES_TABLE, _ANALYSIS_FIELDS, f"id={self._eq(analysis_id)}")
        return rows[0] if rows else None

    def save_certificate(self, certificate: Dict[str, Any]) -> str:
        self._insert(CERTIFICATES_TABLE, {
            "certificate_id": certificate["certificate_id"],
            "analysis_id": certificate["analysis_id"],
            "first_name": certificate["first_name"],
            "surname": certificate["surname"],
            "career": certificate["career"],
            "score": certificate["score"],
            "clerk_user_id": certificate.get("clerk_user_id"),
            "issued_at": certificate["issued_at"],
        })
        return certificate["certificate_id"]

    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        rows = self._select(CERTIFICATES_TABLE, _CERT_FIELDS, f"certificate_id={self._eq(certificate_id)}")
        return rows[0] if rows else None

    def list_certificates_for_user(self, clerk_user_id: str) -> List[Dict[str, Any]]:
        return self._select(
            CERTIFICATES_TABLE, _CERT_FIELDS, f"clerk_user_id={self._eq(clerk_user_id)}", order="issued_at.desc"
        )
