from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)

from core.config import settings
from core.logging import setup_logger
from domain.knowledge import FAQ
from infrastructure.chroma.client import ChromaClient
from interfaces.repositories.knowledge import KnowledgeBaseRepository

logger = setup_logger(__name__)


class ChromaKnowledgeRepository(KnowledgeBaseRepository):
    def __init__(self):
        self.client = ChromaClient.get_instance()
        self.embedding_function = (
            DefaultEmbeddingFunction()
            if settings.EMBEDDING_MODE == "default"
            else OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_EMBEDDING_MODEL,
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function,
        )

    async def find_similar(
        self, query: str, limit: int = 3, similarity_threshold: float = 1.0
    ) -> list[dict]:
        results = self.collection.query(
            query_texts=[query], n_results=limit, include=["metadatas", "distances"]
        )

        similar_documents = []
        for i, (distance, metadata) in enumerate(
            zip(results["distances"][0], results["metadatas"][0])
        ):
            if distance > similarity_threshold:
                continue

            similar_documents.append(
                {
                    "question": metadata["question"],
                    "answer": metadata["answer"],
                    "distance": distance,
                }
            )

        return similar_documents

    async def bulk_add_faqs(self, faqs: list[FAQ]) -> None:
        documents = []
        metadatas = []
        ids = []

        for i, faq in enumerate(faqs):
            documents.append(f"{faq.question}\n{faq.answer}")
            metadatas.append(
                {
                    "question": faq.question,
                    "answer": faq.answer,
                    "tags": ",".join(faq.tags),
                }
            )
            ids.append(f"faq_{i}")

        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            logger.info(
                f"Adding batch {i // batch_size + 1} of {len(documents) // batch_size + 1}"
            )
            self.collection.add(
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
                ids=ids[i : i + batch_size],
            )
