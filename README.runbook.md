# Runbook - W9:D1 Metrics

## Start
make run

## Generate traffic
make load

## Check
- Grafana http://localhost:3000 (no login needed)
- Prometheus http://localhost:9090
- App http://localhost:8000/healthz and /metrics

## Key PromQL
- p95 latency:
  histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
- Error rate (5xx/sec):
  sum(rate(http_requests_total{status_code=~"5.."}[5m]))
- RPS:
  sum(rate(http_requests_total[1m]))

## Tear down
make clean

