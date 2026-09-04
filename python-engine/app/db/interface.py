"""
Repository interface.

The rest of the app talks to storage only through this interface. Phase 1
ships a SQLite-backed implementation (`LocalStore`) so the app runs with
zero external dependencies in development. When Supabase is connected,
implement the same interface against Supabase's Postgres (e.g. via
`postgrest-py` or a direct `psycopg` connection using
SUPABASE_SERVICE_ROLE_KEY on the server side only) and swap it in via the
STORAGE_BACKEND environment variable - no other code needs to change.

The table shapes here intentionally mirror supabase/migrations/*.sql so
the swap is mechanical.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Repository(ABC):
    @abstractmethod
    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        """Persist an analysis record. Returns the analysis id."""

    @abstractmethod
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def save_certificate(self, certificate: Dict[str, Any]) -> str:
        """Persist a certificate record. Returns the certificate_id."""

    @abstractmethod
    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        ...
