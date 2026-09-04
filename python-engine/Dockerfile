# Deployment-readiness only. Not built/deployed as part of Phase 1.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV STORAGE_BACKEND=local
ENV LOCAL_DB_PATH=/app/local_dev.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
