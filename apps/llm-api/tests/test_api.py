"""Unit tests for the LLM API. Ollama is mocked: no model or cluster needed."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FAKE_OLLAMA_RESULT = {
    "response": "Kubernetes orchestrates containers.",
    "eval_count": 20,
    "eval_duration": 4_000_000_000,  # 4 s -> 5 tokens/s
}


def test_health_is_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_ready_503_when_ollama_down(monkeypatch):
    async def fake_ready(self):
        return False

    monkeypatch.setattr("app.api.health_routes.OllamaClient.is_ready", fake_ready)
    assert client.get("/ready").status_code == 503


def test_ready_200_when_ollama_up(monkeypatch):
    async def fake_ready(self):
        return True

    monkeypatch.setattr("app.api.health_routes.OllamaClient.is_ready", fake_ready)
    assert client.get("/ready").status_code == 200


def test_chat_returns_text_and_token_stats(monkeypatch):
    async def fake_generate(self, prompt):
        return FAKE_OLLAMA_RESULT

    monkeypatch.setattr(
        "app.infrastructure.ollama_client.OllamaClient.generate", fake_generate
    )
    r = client.post("/chat", json={"prompt": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["response"] == FAKE_OLLAMA_RESULT["response"]
    assert body["generated_tokens"] == 20
    assert body["tokens_per_second"] == 5.0


def test_chat_upstream_error_does_not_leak_details(monkeypatch):
    async def boom(self, prompt):
        raise RuntimeError("secret-internal-host:11434 refused")

    monkeypatch.setattr("app.infrastructure.ollama_client.OllamaClient.generate", boom)
    r = client.post("/chat", json={"prompt": "hi"})
    assert r.status_code == 502
    assert "secret-internal-host" not in r.text


def test_chat_rejects_missing_prompt():
    assert client.post("/chat", json={}).status_code == 422


def test_metrics_endpoint_exposes_llm_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "llm_generated_tokens_total" in r.text


@pytest.mark.asyncio
async def test_ollama_payload_is_deterministic(monkeypatch):
    """Experiment-validity check: temperature/seed/num_predict are always sent."""
    from app.core.config import settings
    from app.infrastructure.ollama_client import OllamaClient

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"response": "ok"})

    transport = httpx.MockTransport(handler)
    real_client = httpx.AsyncClient

    def patched(*args, **kwargs):
        return real_client(*args, transport=transport, **kwargs)

    monkeypatch.setattr("app.infrastructure.ollama_client.httpx.AsyncClient", patched)

    await OllamaClient().generate("test prompt")

    assert captured["stream"] is False
    assert captured["options"]["temperature"] == settings.LLM_TEMPERATURE == 0.0
    assert captured["options"]["seed"] == settings.LLM_SEED
    assert captured["options"]["num_predict"] == settings.LLM_NUM_PREDICT
    assert captured["keep_alive"] == settings.LLM_KEEP_ALIVE
