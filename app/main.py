from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry, multiprocess, Gauge
from prometheus_client import PROCESS_COLLECTOR, PLATFORM_COLLECTOR
import time, random, logging, os

# --- logging (plain JSON-ish) ---
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
log = logging.getLogger("w9")

app = FastAPI(title="W9-D1 FastAPI with Prometheus")

# --- metrics registry ---
registry = CollectorRegistry()
# Include default process & platform collectors
PROCESS_COLLECTOR(registry)
PLATFORM_COLLECTOR(registry)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
    registry=registry
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency (seconds)",
    ["method", "path", "status_code"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
    registry=registry
)

INPROGRESS = Gauge(
    "inprogress_requests",
    "In-progress requests",
    ["path"],
    registry=registry
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
    """
    Simulate a prediction endpoint.
    q controls latency: higher q -> slightly slower (to see p95 move).
    """
    simulated = random.random()
    # base 10-50ms + extra based on q
    base_ms = random.randint(10, 50)
    time.sleep((base_ms/1000.0) + (q * 0.05))  # up to ~100ms extra
    log.info(f"/predict served in_ms={base_ms} q={q} rand={simulated}")
    return {"prediction": 1 if simulated > q else 0, "q": q}

@app.get("/error")
def error():
    # Force an error to see error-rate on dashboards
    raise ValueError("simulated failure for monitoring demo")

@app.get("/metrics")
def metrics():
    return JSONResponse(
        content=generate_latest(registry).decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )

