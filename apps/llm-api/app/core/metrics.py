from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_requests_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=["method", "path"],
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 15, 30, 60, 120),
)
