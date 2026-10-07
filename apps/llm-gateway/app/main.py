import hmac
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.config import Settings

logger = logging.getLogger("llm-gateway")

# Only these routes are exposed. Everything else (docs, openapi, /metrics) is
# blocked at the gateway even for authenticated clients.
ALLOWED_ROUTES = {
    ("POST", "/chat"),
    ("GET", "/health"),
    ("GET", "/ready"),
}

# Headers copied to the upstream. "authorization" is deliberately NOT forwarded.
FORWARDED_REQUEST_HEADERS = ("content-type", "accept", "x-request-id")
FORWARDED_RESPONSE_HEADERS = ("content-type", "x-request-id")

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


def is_authorized(header_value: str | None, api_key: str) -> bool:
    """Check "Authorization: Bearer <key>" with a constant-time comparison."""
    if not header_value:
        return False

    scheme, _, token = header_value.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return False

    return hmac.compare_digest(token.encode(), api_key.encode())


def create_app(
    settings: Settings | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # One shared client: connections to the upstream are reused.
        app.state.client = httpx.AsyncClient(
            base_url=settings.UPSTREAM_URL,
            timeout=settings.REQUEST_TIMEOUT,
            transport=transport,
        )
        yield
        await app.state.client.aclose()

    app = FastAPI(
        title="LLM Gateway",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.get("/_gateway/health", include_in_schema=False)
    async def gateway_health():
        # Used only by Kubernetes probes; carries no data and needs no key.
        return {"status": "healthy"}

    @app.api_route("/{path:path}", methods=HTTP_METHODS, include_in_schema=False)
    async def proxy(path: str, request: Request):
        if not is_authorized(request.headers.get("authorization"), settings.API_KEY):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        if (request.method, "/" + path) not in ALLOWED_ROUTES:
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        headers = {
            name: value
            for name, value in request.headers.items()
            if name.lower() in FORWARDED_REQUEST_HEADERS
        }

        try:
            upstream = await request.app.state.client.request(
                request.method,
                "/" + path,
                content=await request.body(),
                headers=headers,
            )
        except httpx.TimeoutException:
            return JSONResponse(status_code=504, content={"detail": "Upstream timeout"})
        except httpx.HTTPError:
            logger.exception("upstream request failed")
            return JSONResponse(
                status_code=502, content={"detail": "Upstream unavailable"}
            )

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers={
                name: upstream.headers[name]
                for name in FORWARDED_RESPONSE_HEADERS
                if name in upstream.headers
            },
        )

    return app


app = create_app()
