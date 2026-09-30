from app.infrastructure.ollama_client import OllamaClient


class ChatService:
    def __init__(self):
        self.client = OllamaClient()

    async def chat(self, prompt: str):
        return await self.client.generate(prompt)
