from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from core.config import settings
from infrastructure.openai.client import get_openai_client
from interfaces.services.llm import LLMService


class OpenAIService(LLMService):
    def __init__(self):
        self.client = get_openai_client()
        self.chat_model = settings.OPENAI_CHAT_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | str:
        response = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=temperature,
            stream=stream,
        )

        if stream:
            return response

        return response.choices[0].message.content.strip()
