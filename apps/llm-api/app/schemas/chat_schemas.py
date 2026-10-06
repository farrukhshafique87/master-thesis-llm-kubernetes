from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str
    generated_tokens: int | None = None
    tokens_per_second: float | None = None
