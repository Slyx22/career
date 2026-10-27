"""SupabaseStore against a small fake of Supabase's REST API, so the
request shapes are checked without a real Supabase project."""
from urllib.parse import parse_qs, unquote, urlparse

import pytest

from app.db.supabase_store import SupabaseStore, StorageError


class _Resp:
    def __init__(self, status, data=None, text=""):
        self.status_code = status
        self._data = data
        self.text = text

    def json(self):
        return self._data


class FakePostgrest:
    def __init__(self):
        self.tables = {"engine_analyses": [], "engine_certificates": []}
        self.seen_headers = []

    def post(self, url, json, headers, timeout):
        self.seen_headers.append(headers)
        table = urlparse(url).path.rsplit("/", 1)[-1]
        if table not in self.tables:
            return _Resp(404, text="relation does not exist")
        self.tables[table].append(dict(json))
        return _Resp(201)

    def get(self, url, headers, timeout):
        self.seen_headers.append(headers)
        parsed = urlparse(url)
        table = parsed.path.rsplit("/", 1)[-1]
        qs = parse_qs(parsed.query)
        rows = list(self.tables[table])
        for key, (value,) in qs.items():
            if key in ("select", "order"):
                continue
            assert value.startswith("eq.")
            rows = [r for r in rows if str(r.get(key)) == unquote(value[3:])]
        if "order" in qs:
            field, direction = qs["order"][0].split(".")
            rows.sort(key=lambda r: r[field], reverse=direction == "desc")
        return _Resp(200, rows)


@pytest.fixture
def store():
    return SupabaseStore("https://example.supabase.co", "sb_secret_test", session=FakePostgrest())


def _analysis(i="a1"):
    return {"id": i, "first_name": "Rayn", "surname": "Miles", "career": "Software Developers",
            "score": 72, "payload": {"strengths": ["Programming"]}, "created_at": "2026-10-27T10:00:00+00:00"}


def _cert(cid, issued, user="user_1"):
    return {"certificate_id": cid, "analysis_id": "a1", "first_name": "Rayn", "surname": "Miles",
            "career": "Software Developers", "score": 72, "clerk_user_id": user, "issued_at": issued}


def test_round_trip_analysis_and_certificates(store):
    store.save_analysis(_analysis())
    assert store.get_analysis("a1")["payload"] == {"strengths": ["Programming"]}
    assert store.get_analysis("missing") is None

    store.save_certificate(_cert("CR-AAA11111", "2026-10-01T00:00:00+00:00"))
    store.save_certificate(_cert("CR-BBB22222", "2026-10-20T00:00:00+00:00"))
    store.save_certificate(_cert("CR-CCC33333", "2026-10-21T00:00:00+00:00", user="someone_else"))

    assert store.get_certificate("CR-AAA11111")["score"] == 72
    assert store.get_certificate("CR-NOPE0000") is None
    mine = store.list_certificates_for_user("user_1")
    assert [c["certificate_id"] for c in mine] == ["CR-BBB22222", "CR-AAA11111"]


def test_new_style_secret_key_is_not_sent_as_bearer(store):
    store.get_certificate("CR-X")
    headers = store.session.seen_headers[-1]
    assert headers["apikey"] == "sb_secret_test"
    assert "Authorization" not in headers


def test_legacy_jwt_key_is_sent_as_bearer():
    s = SupabaseStore("https://x.supabase.co", "eyJhbGciOi.test", session=FakePostgrest())
    assert s.headers["Authorization"] == "Bearer eyJhbGciOi.test"


def test_missing_table_raises_clear_error():
    s = SupabaseStore("https://x.supabase.co", "sb_secret_test", session=FakePostgrest())
    s.session.tables.pop("engine_analyses")
    with pytest.raises(StorageError):
        s.save_analysis(_analysis())


def test_backend_selection(monkeypatch):
    from app.db import local_store

    for k in ("STORAGE_BACKEND", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE"):
        monkeypatch.delenv(k, raising=False)
    assert local_store.storage_backend_name() == "local"
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "sb_secret_x")
    assert local_store.storage_backend_name() == "supabase"
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    assert local_store.storage_backend_name() == "local"
