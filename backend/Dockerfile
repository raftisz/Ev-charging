FROM python:3.12-slim

WORKDIR /app

# System deps needed for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
# Build context is the project root (see docker-compose.yml) so the
# static site can be copied in and served directly from /app/docs
COPY docs ./docs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
