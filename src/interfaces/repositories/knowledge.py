from abc import ABC, abstractmethod

from domain.knowledge import NaverFAQ


class KnowledgeBaseRepository(ABC):
    @abstractmethod
    async def find_similar(
        self, query: str, limit: int = 3, distance_threshold: float = 0.5
    ) -> list[dict]:
        pass

    @abstractmethod
    async def bulk_add_faqs(self, faqs: list[NaverFAQ]) -> None:
        pass
