import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = logging.getLogger("llm-api")

router = APIRouter()

service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await service.chat(request.prompt)

    except Exception as e:
        # Log details server-side; do not leak internals to the client.
        logger.exception("chat request failed")
        raise HTTPException(status_code=502, detail="Upstream LLM error") from e
