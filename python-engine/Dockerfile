# Deployment-readiness only. Not built/deployed as part of Phase 1.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Storage is chosen automatically: DATABASE_URL -> Postgres (permanent),
# else Supabase API keys, else the temporary SQLite file (app/db/local_store.py).
ENV STORAGE_BACKEND=auto
ENV LOCAL_DB_PATH=/app/local_dev.db

EXPOSE 8000

# Render assigns a port via $PORT; fall back to 8000 for local/docker runs.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
