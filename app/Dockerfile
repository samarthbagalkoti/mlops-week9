# ./app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# App deps
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt \
    && pip install "uvicorn[standard]" fastapi prometheus-client

# App code
COPY . .

EXPOSE 8000

# IMPORTANT: bind to 0.0.0.0 so the port mapping works
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

