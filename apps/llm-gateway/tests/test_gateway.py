"""Unit tests for the gateway. The upstream FastAPI service is mocked."""

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app, is_authorized

KEY = "test-api-key-0123456789abcdef"
AUTH = {"Authorization": f"Bearer {KEY}"}

seen: list[httpx.Request] = []


def upstream_handler(request: httpx.Request) -> httpx.Response:
    seen.append(request)
    if request.url.path == "/chat":
        return httpx.Response(200, json={"response": "hello"})
    if request.url.path == "/ready":
        return httpx.Response(503, json={"status": "not_ready"})
    return httpx.Response(200, json={"status": "healthy"})


def make_client(handler=upstream_handler) -> TestClient:
    seen.clear()
    app = create_app(
        Settings(API_KEY=KEY, UPSTREAM_URL="http://upstream"),
        transport=httpx.MockTransport(handler),
    )
    return TestClient(app)


def test_gateway_health_needs_no_key():
    with make_client() as c:
        assert c.get("/_gateway/health").status_code == 200


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer wrong-key-0123456789"},
        {"Authorization": KEY},
        {"Authorization": f"Basic {KEY}"},
        {"Authorization": "Bearer "},
    ],
)
def test_requests_without_valid_key_are_rejected(headers):
    with make_client() as c:
        assert c.post("/chat", json={"prompt": "x"}, headers=headers).status_code == 401
        assert seen == []  # nothing reached the upstream


def test_valid_key_proxies_chat_and_hides_authorization():
    with make_client() as c:
        r = c.post("/chat", json={"prompt": "hi"}, headers=AUTH)
    assert r.status_code == 200
    assert r.json() == {"response": "hello"}
    assert len(seen) == 1
    assert seen[0].url.path == "/chat"
    assert b"hi" in seen[0].content
    assert "authorization" not in seen[0].headers


def test_valid_key_proxies_health():
    with make_client() as c:
        r = c.get("/health", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_upstream_status_is_passed_through():
    with make_client() as c:
        assert c.get("/ready", headers=AUTH).status_code == 503


@pytest.mark.parametrize("path", ["/metrics", "/docs", "/openapi.json", "/admin"])
def test_non_allowlisted_paths_are_blocked_even_with_key(path):
    with make_client() as c:
        assert c.get(path, headers=AUTH).status_code == 404
    assert seen == []


def test_wrong_method_on_allowed_path_is_blocked():
    with make_client() as c:
        assert c.get("/chat", headers=AUTH).status_code == 404


def test_upstream_down_returns_502():
    def boom(request):
        raise httpx.ConnectError("refused")

    with make_client(boom) as c:
        assert c.get("/health", headers=AUTH).status_code == 502


def test_upstream_timeout_returns_504():
    def slow(request):
        raise httpx.ReadTimeout("slow")

    with make_client(slow) as c:
        assert c.post("/chat", json={"prompt": "x"}, headers=AUTH).status_code == 504


def test_short_api_key_is_refused_at_startup():
    with pytest.raises(ValidationError):
        Settings(API_KEY="short")


def test_is_authorized_unit():
    assert is_authorized(f"Bearer {KEY}", KEY)
    assert is_authorized(f"bearer {KEY}", KEY)
    assert not is_authorized(None, KEY)
    assert not is_authorized("Bearer nope", KEY)
