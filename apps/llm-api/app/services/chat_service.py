from app.core.metrics_definitions import GENERATED_TOKENS, TOKENS_PER_SECOND
from app.infrastructure.ollama_client import OllamaClient
from app.schemas.chat_schemas import ChatResponse

NS_PER_SECOND = 1_000_000_000


class ChatService:
    def __init__(self):
        self.client = OllamaClient()

    async def chat(self, prompt: str) -> ChatResponse:
        result = await self.client.generate(prompt)

        tokens = result.get("eval_count")
        eval_ns = result.get("eval_duration")
        tokens_per_second = None

        if tokens:
            GENERATED_TOKENS.inc(tokens)

        if tokens and eval_ns:
            tokens_per_second = round(tokens / (eval_ns / NS_PER_SECOND), 3)
            TOKENS_PER_SECOND.observe(tokens_per_second)

        return ChatResponse(
            response=result["response"],
            generated_tokens=tokens,
            tokens_per_second=tokens_per_second,
        )
