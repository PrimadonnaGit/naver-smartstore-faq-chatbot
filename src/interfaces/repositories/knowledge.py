from abc import ABC, abstractmethod

from domain.knowledge import FAQ


class KnowledgeBaseRepository(ABC):
    @abstractmethod
    async def find_similar(
        self, query: str, limit: int = 3, similarity_threshold: float = 0.5
    ) -> list[dict]:
        pass

    @abstractmethod
    async def bulk_add_faqs(self, faqs: list[FAQ]) -> None:
        pass
