import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class OllamaClient:
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8)
    )
    async def generate(self, prompt: str):
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            response.raise_for_status()

            return response.json()["response"]

    async def is_ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.OLLAMA_URL}/api/tags")

                response.raise_for_status()

            return True

        except (httpx.HTTPError, httpx.RequestError):
            return False
