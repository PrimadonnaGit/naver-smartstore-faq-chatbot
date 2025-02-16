from abc import ABC, abstractmethod

from domain.chat import Message


class ChatMemoryRepository(ABC):
    @abstractmethod
    async def save_message(self, session_id: str, message: Message) -> None:
        pass

    @abstractmethod
    async def get_recent_messages(
        self, session_id: str, limit: int = 10
    ) -> list[Message]:
        pass
