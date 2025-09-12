import requests, time

def test_metrics_endpoint_up():
    # start compose first; then run this test in CI to at least check the app
    for _ in range(10):
        try:
            r = requests.get("http://0.0.0.0:8001/metrics", timeout=2)
            assert r.status_code == 200
            assert "http_requests_total" in r.text
            return
        except Exception:
            time.sleep(1)
    raise AssertionError("metrics endpoint not reachable")

