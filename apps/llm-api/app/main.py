from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import settings
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.metrics import metrics_middleware
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.middleware("http")(metrics_middleware)

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
