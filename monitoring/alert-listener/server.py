from flask import Flask, request
import logging, sys, json, os
os.makedirs("/var/log/alerts", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("/var/log/alerts/alerts.log")],
    format="%(asctime)s %(levelname)s %(message)s"
)
app = Flask(__name__)

@app.get("/healthz")
def healthz(): return "ok", 200

@app.post("/webhook")
def webhook():
    logging.info("ALERT %s", json.dumps(request.json))
    return "", 200

