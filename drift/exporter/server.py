import os, threading, time, json
import pandas as pd
from fastapi import FastAPI, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

DATA_DIR = os.environ.get("DATA_DIR", "/data")
REPORT_DIR = os.environ.get("REPORT_DIR", "/reports")
REF_PATH = os.path.join(DATA_DIR, "reference.csv")
CUR_PATH = os.path.join(DATA_DIR, "current.csv")
DATASET_LABEL = os.environ.get("DATASET_LABEL", "demo")
INTERVAL_SEC = int(os.environ.get("EVAL_INTERVAL_SEC", "15"))

os.makedirs(REPORT_DIR, exist_ok=True)

app = FastAPI(title="Evidently Drift Exporter")

registry = CollectorRegistry()
g_dataset_drift = Gauge("evidently_dataset_drift", "Dataset drift detected (0/1)", ["dataset"], registry=registry)
g_share_drifted = Gauge("evidently_share_drifted_columns", "Share of drifted columns (0..1)", ["dataset"], registry=registry)
g_n_drifted = Gauge("evidently_n_drifted_columns", "Number of drifted columns", ["dataset"], registry=registry)
g_target_drift = Gauge("evidently_target_drift", "Target drift detected (0/1)", ["dataset"], registry=registry)
g_rows_ref = Gauge("evidently_rows_reference", "Rows in reference", ["dataset"], registry=registry)
g_rows_cur = Gauge("evidently_rows_current", "Rows in current", ["dataset"], registry=registry)

latest_html = "<html><body><h3>No report yet</h3></body></html>"
latest_json = {}

def compute_and_publish():
    global latest_html, latest_json
    if not (os.path.exists(REF_PATH) and os.path.exists(CUR_PATH)):
        return
    ref = pd.read_csv(REF_PATH)
    cur = pd.read_csv(CUR_PATH)

    report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
    report.run(reference_data=ref, current_data=cur)
    latest_json = report.as_dict()
    html_path = os.path.join(REPORT_DIR, "drift_report.html")
    json_path = os.path.join(REPORT_DIR, "drift_report.json")
    report.save_html(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        latest_html = f.read()
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(latest_json, jf, ensure_ascii=False)

    # Pull top-level dataset drift metrics from DataDriftPreset output
    # Find the DataDriftPreset result block
    dd = None
    for m in latest_json.get("metrics", []):
        if m.get("metric") == "DataDriftPreset":
            dd = m.get("result", {})
            break

    dataset_drift = 1.0 if dd and dd.get("dataset_drift") else 0.0
    share = float(dd.get("share_of_drifted_columns", 0.0)) if dd else 0.0
    ncols = int(dd.get("number_of_drifted_columns", 0)) if dd else 0

    # Target drift block
    td = None
    for m in latest_json.get("metrics", []):
        if m.get("metric") == "TargetDriftPreset":
            td = m.get("result", {})
            break
    target_drift = 1.0 if td and td.get("drift_detected") else 0.0

    g_dataset_drift.labels(DATASET_LABEL).set(dataset_drift)
    g_share_drifted.labels(DATASET_LABEL).set(share)
    g_n_drifted.labels(DATASET_LABEL).set(ncols)
    g_target_drift.labels(DATASET_LABEL).set(target_drift)
    g_rows_ref.labels(DATASET_LABEL).set(len(ref))
    g_rows_cur.labels(DATASET_LABEL).set(len(cur))

def loop_worker():
    while True:
        try:
            compute_and_publish()
        except Exception as e:
            # swallow errors to keep exporter alive
            print("[exporter] error:", e, flush=True)
        time.sleep(INTERVAL_SEC)

@app.on_event("startup")
def start_bg():
    threading.Thread(target=loop_worker, daemon=True).start()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/report")
def report():
    return Response(latest_html, media_type="text/html")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

