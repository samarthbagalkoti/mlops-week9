# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import Response  # <-- add this
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
import time, random, logging

# ... (rest unchanged)

@app.get("/metrics")
def metrics():
    # return raw bytes with correct content-type
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

