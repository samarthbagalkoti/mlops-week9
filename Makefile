APP?=w9-app

.PHONY: setup run load open test clean

setup:
	@echo "Nothing to setup. Ensure Docker Desktop is running."

run:
	docker compose up -d --build
	@sleep 5
	@echo "App:        http://localhost:8000/healthz"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana:    http://localhost:3000"

load:
	docker run --rm --network host -v $$PWD/load:/scripts grafana/k6 run /scripts/script.js || \\
	k6 run load/script.js

open:
	@python -c "import webbrowser; webbrowser.open('http://localhost:3000')"

test:
	pytest -q

clean:
	docker compose down -v

