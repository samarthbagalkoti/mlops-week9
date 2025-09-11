**Problem:** Need production-grade visibility (RPS, errors, p95) for ML microservices.
**Architecture:** FastAPI → Prometheus scrape (/metrics) → Grafana dashboard.
**Choices:** Prometheus histograms for quantiles; Grafana for SLO views; local Compose for speed.
**Costs:** Local dev ≈ free; EKS move later uses managed node costs + small PVCs for Prom/Grafana.
**Risks:** Incorrect metric labels can balloon cardinality; keep labels minimal (method,path,status_code).
**Next steps:** W9:D2 add alerts (p95>200ms); D3 Evidently drift; D4 logs (Fluentd/CloudWatch); D7 demo + alert proof.

