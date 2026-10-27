# Render — Deploy the Python backend

Copy these exact values into the **Render Web Service** form:

| Field | Value |
|---|---|
| **Root Directory** | `python-engine` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Dockerfile Path** | `python-engine/Dockerfile` |
| **Instance Type** | Free (or the cheapest) |

> **Note on the start command:** `app.main:app` is correct, NOT `main:app`.
> The FastAPI app lives at `python-engine/app/main.py`, so the module path
> inside the container is `app.main`. The old guide had `main:app` which is
> wrong and will fail with "No module named 'main'".

## After creating the service

1. Wait ~1-2 minutes for Render to build and start.
2. Open the URL Render gives you (e.g. `https://career-xxx.onrender.com`)
   and append `/health` → you should see `{"status":"ok","storage":"supabase"}`
   (`"local"` means certificates are not being kept permanently).
3. **Copy that URL** — you need it for Vercel in the next step.

## Environment variables on Render

In your Render service → **Environment Variables**, add:

| Key | Value |
|---|---|
| `ALLOWED_ORIGINS` | `https://srmaps.co.za,http://localhost:3000` |
| `PUBLIC_VERIFY_URL_BASE` | `https://srmaps.co.za` |
| `DATABASE_URL` | Postgres connection string for the low-privilege `engine_store` role in Supabase (via the session pooler, `aws-0-eu-west-1.pooler.supabase.com:5432`). Preferred. |
| `STORAGE_BACKEND` | `auto` |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | Alternative to `DATABASE_URL`: Supabase Project URL and **secret** key. Never put the key in the frontend. |
| `REQUIRE_ACCOUNT_FOR_CERTIFICATE` | `false` |

Do **not** set `STORAGE_BACKEND=local` in production: it forces the
temporary SQLite file, which Render wipes on every restart, deleting all
certificates. With `DATABASE_URL` (or the two Supabase values) set, the engine stores
analyses and certificates permanently in Supabase. Before the first
deploy with them, run `supabase/migrations/0006_engine_storage.sql` once
in Supabase → SQL Editor. Check it worked: `/health` shows
`"storage":"postgres"` (or `"supabase"`).

Then **Redeploy** the service so the new env vars take effect.