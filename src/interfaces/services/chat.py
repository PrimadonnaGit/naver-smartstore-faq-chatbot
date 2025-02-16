from abc import ABC, abstractmethod
from typing import AsyncGenerator

from domain.chat import ChatResponse


class ChatService(ABC):
    @abstractmethod
    async def process_message(
        self, session_id: str, message: str
    ) -> AsyncGenerator[ChatResponse, None]:
        pass

    @abstractmethod
    async def get_welcome_message(self) -> ChatResponse:
        pass

    @abstractmethod
    async def is_smartstore_related(self, message: str) -> bool:
        pass

    @abstractmethod
    async def get_follow_up_message(self, query: str, answer: str) -> ChatResponse:
        pass

    @abstractmethod
    async def create_chat_completion(
        self, query: str, chat_history: list[str], knowledge_context: str
    ) -> AsyncGenerator[str, None]:
        pass
