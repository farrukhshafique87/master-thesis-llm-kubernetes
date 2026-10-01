from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.infrastructure.ollama_client import OllamaClient

router = APIRouter()

ollama_client = OllamaClient()


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/ready")
async def ready():
    if await ollama_client.is_ready():
        return {"status": "ready"}

    return JSONResponse(
        status_code=503,
        content={"status": "not_ready"},
    )
