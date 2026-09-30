from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await service.chat(request.prompt)

        return ChatResponse(response=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
