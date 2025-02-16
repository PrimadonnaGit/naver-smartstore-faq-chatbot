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
