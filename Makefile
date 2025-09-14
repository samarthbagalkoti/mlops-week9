APP?=w9-app
APP_URL ?= http://localhost:8001
ALERT_BURST ?= 30
SLOW_REQS   ?= 60
SHELL := /bin/bash
PY ?= python3

PY ?= .venv/bin/python

.PHONY: setup
setup:
	@test -x .venv/bin/python || python3 -m venv .venv
	@.venv/bin/python -m pip install --upgrade pip
	@.venv/bin/pip install -r requirements.txt
.PHONY: setup run load open test clean
.PHONY: drift.trigger

setup:
	@echo "Nothing to setup. Ensure Docker Desktop is running."

run:
	docker compose up -d --build
	@sleep 5
	@echo "App:        http://0.0.0.0:8001/healthz"
	@echo "Prometheus: http://0.0.0.0:9091"
	@echo "Grafana:    http://0.0.0.0:3001"

load:
	docker run --rm --network host -v $$PWD/load:/scripts grafana/k6 run /scripts/script.js || \\
	k6 run load/script.js

open:
	@if command -v xdg-open >/dev/null 2>&1; then xdg-open http://0.0.0.0:3001; \
	elif command -v open >/dev/null 2>&1; then open http://0.0.0.0:3001; \
	elif command -v python3 >/dev/null 2>&1; then python3 -c "import webbrowser; webbrowser.open('http://0.0.0.0:3001')"; \
	elif command -v python >/dev/null 2>&1; then python -c "import webbrowser; webbrowser.open('http://0.0.0.0:3001')"; \
	else echo "Open http://0.0.0.0:3001 in your browser."; fi

test:
	pytest -q

clean:
	docker compose down -v


alerts.up:
	docker compose up -d --build
	@sleep 8
	@echo "Prometheus:    http://0.0.0.0:9091"
	@echo "Alertmanager:  http://0.0.0.0:9093"
	@echo "Listener:      http://0.0.0.0:5001/healthz"
	@echo "Grafana:       http://0.0.0.0:3001"

alerts.tail:
	@mkdir -p monitoring/alert-listener-data
	@touch monitoring/alert-listener-data/alerts.log
	tail -F --retry monitoring/alert-listener-data/alerts.log


# Traffic that should trigger both latency & errors
alerts.fire:
	@echo "# burst some errors"
	@for i in $$(seq 1 $(ALERT_BURST)); do \
		curl -s -o /dev/null -w "%{http_code}\n" "$(APP_URL)/error" || true; \
	done
	@echo "# slow predictions to push p95 > 200ms"
	@for i in $$(seq 1 $(SLOW_REQS)); do \
		curl -s "$(APP_URL)/predict?q=0.95" > /dev/null || true; \
	done

alerts.clean:
	docker compose down -v
	rm -f monitoring/alert-listener-data/alerts.log || true

drift.up:
	docker compose up -d --build
	@sleep 8
	@echo "Exporter:   http://localhost:8001/healthz"
	@echo "Report:     http://localhost:8001/report"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana:    http://localhost:3000"

drift.view:
	@python3 -c "import webbrowser; webbrowser.open('http://localhost:8002/report')"

drift.sim:
	@echo "Simulating alternating healthy vs drifted windows (already running in container)."

# your existing target, now uses venv python
drift.trigger: setup
	@$(PY) -c 'import os,pandas as pd,numpy as np; from sklearn.datasets import make_classification; os.makedirs("data",exist_ok=True); X,y=make_classification(n_samples=600,n_features=6,n_informative=4,random_state=7,class_sep=0.5); X[:,0]+=0.8; X[:,1]+=0.5; pd.DataFrame(X,columns=["f{}".format(i) for i in range(6)]).assign(target=y).to_csv("data/current.csv",index=False); print("wrote data/current.csv (forced drift)")'


drift.clean:
	docker compose down -v
	rm -rf data/*.csv reports/*

