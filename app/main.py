# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    PROCESS_COLLECTOR, PLATFORM_COLLECTOR,
)
import time, random, logging

# --- logging (plain JSON-ish) ---
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
log = logging.getLogger("w9")

# Instantiate app FIRST
app = FastAPI(title="W9-D1 FastAPI with Prometheus")

# --- metrics registry ---
registry = CollectorRegistry()
PROCESS_COLLECTOR(registry)
PLATFORM_COLLECTOR(registry)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency (seconds)",
    ["method", "path", "status_code"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
    registry=registry,
)

INPROGRESS = Gauge(
    "inprogress_requests",
    "In-progress requests",
    ["path"],
    registry=registry,
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    start = time.time()
    INPROGRESS.labels(path=path).inc()
    try:
        response = await call_next(request)
        status = response.status_code
        latency = time.time() - start
        REQUEST_COUNT.labels(method=method, path=path, status_code=str(status)).inc()
        REQUEST_LATENCY.labels(method=method, path=path, status_code=str(status)).observe(latency)
        return response
    finally:
        INPROGRESS.labels(path=path).dec()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/predict")
def predict(q: float = 0.5):
    simulated = random.random()
    base_ms = random.randint(10, 50)
    time.sleep((base_ms/1000.0) + (q * 0.05))
    log.info(f"/predict served in_ms={base_ms} q={q} rand={simulated}")
    return {"prediction": 1 if simulated > q else 0, "q": q}

@app.get("/error")
def error():
    raise ValueError("simulated failure for monitoring demo")

@app.get("/metrics")
def metrics():
    # Prometheus expects plain text format (not JSON)
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

