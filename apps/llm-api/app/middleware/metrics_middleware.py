import time

from fastapi import Request

from app.core.metrics_definitions import REQUEST_COUNTER, REQUEST_LATENCY


async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    path = request.url.path
    method = request.method
    status_code = str(response.status_code)

    REQUEST_COUNTER.labels(
        method=method,
        path=path,
        status_code=status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        method=method,
        path=path,
    ).observe(duration)

    return response
