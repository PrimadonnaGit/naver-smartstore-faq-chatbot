from abc import ABC, abstractmethod

from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class LLMService(ABC):
    @abstractmethod
    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | str:
        pass

    @abstractmethod
    async def is_smartstore_related(self, query: str) -> bool:
        pass
