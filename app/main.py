import time, random
from fastapi import FastAPI, Response, status
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/error")
def error():
    return Response("boom", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/predict")
def predict(q: float = 0.5):
    # simulate p95 latency spikes: sleep more when q is high
    delay = 0.05 + (q * random.uniform(0.15, 0.35))  # ~200–400ms at q=0.95
    time.sleep(delay)
    return {"delay_s": delay}

