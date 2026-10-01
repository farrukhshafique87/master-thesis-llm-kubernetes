import json
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("llm-api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_seconds": round(duration, 4),
                    "timestamp": time.time(),
                }
            )
        )

        return response
