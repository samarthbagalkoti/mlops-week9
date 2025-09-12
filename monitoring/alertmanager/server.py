from flask import Flask, request
import json, time, sys

app = Flask(__name__)

@app.post("/alert")
def alert():
    payload = request.get_json(force=True, silent=True) or {}
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + json.dumps(payload)
    print("ALERT_RECEIVED", line, flush=True)
    with open("/data/alerts.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

