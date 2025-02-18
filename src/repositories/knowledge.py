import asyncio

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)

from core.config import settings
from core.decorators import log_execution_time
from core.enums import CollectionType
from core.logging import setup_logger
from domain.knowledge import NaverFAQ, SearchResult
from infrastructure.chroma.client import ChromaClient
from interfaces.repositories.knowledge import KnowledgeBaseRepository

logger = setup_logger(__name__)


class ChromaKnowledgeRepository(KnowledgeBaseRepository):
    def __init__(self):
        self.client = ChromaClient.get_instance()
        self.embedding_function = (
            OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_EMBEDDING_MODEL,
            )
            if settings.EMBEDDING_MODE == "openai"
            else DefaultEmbeddingFunction()
        )
        self.collections = self._initialize_collections()
        self.weights = {
            CollectionType.FULL: 1.0,
            CollectionType.QUESTION: 0.8,
            CollectionType.ANSWER: 0.6,
        }

    def _initialize_collections(self) -> dict:
        collections = {}
        for col_type in CollectionType:
            collection_name = f"{settings.CHROMA_COLLECTION_NAME}_{col_type.value}"
            collections[col_type] = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
            )
        return collections

    @log_execution_time
    async def find_similar(
        self, query: str, limit: int = 3, distance_threshold: float = 1.0
    ) -> list[dict]:
        search_tasks = [
            self._search_collection(
                collection_type=col_type,
                query_text=query,
                limit=limit,
                threshold=distance_threshold,
            )
            for col_type in CollectionType
        ]

        results = await asyncio.gather(*search_tasks)

        weighted_results = self._combine_results(results)

        return weighted_results[:limit]

    async def _search_collection(
        self,
        collection_type: CollectionType,
        query_text: str,
        limit: int,
        threshold: float,
    ) -> list[SearchResult]:
        collection = self.collections[collection_type]
        results = collection.query(
            query_texts=[query_text],
            n_results=limit,
            include=["metadatas", "distances"],
        )

        search_results = []
        for i, (distance, metadata) in enumerate(
            zip(results["distances"][0], results["metadatas"][0])
        ):
            if distance > threshold:
                continue

            search_results.append(
                SearchResult(
                    question=metadata["question"],
                    answer=metadata["answer"],
                    score=1 - distance,
                    collection_type=collection_type,
                )
            )

        return search_results

    def _combine_results(self, results: list[list[SearchResult]]) -> list[dict]:
        combined_scores = {}
        for result_group in results:
            for result in result_group:
                key = (result.question, result.answer)
                weight = self.weights[result.collection_type]
                if key not in combined_scores:
                    combined_scores[key] = 0
                combined_scores[key] += result.score * weight

        sorted_results = sorted(
            combined_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"question": question, "answer": answer, "score": score}
            for (question, answer), score in sorted_results
        ]

    @log_execution_time
    async def bulk_add_faqs(self, faqs: list[NaverFAQ]) -> None:
        for collection_type in CollectionType:
            documents = []
            metadatas = []
            ids = []

            for i, faq in enumerate(faqs):
                doc_content = self._get_document_content(faq, collection_type)
                documents.append(doc_content)
                metadatas.append(
                    {
                        "question": faq.question,
                        "answer": faq.answer,
                        "tags": ",".join(faq.tags),
                    }
                )
                ids.append(f"{collection_type.value}_{i}")

            await self._batch_add_to_collection(
                collection_type, documents, metadatas, ids
            )

    def _get_document_content(
        self, faq: NaverFAQ, collection_type: CollectionType
    ) -> str:
        if collection_type == CollectionType.FULL:
            return f"{faq.question}\n{faq.answer}"
        elif collection_type == CollectionType.QUESTION:
            return faq.question
        elif collection_type == CollectionType.ANSWER:
            return faq.answer
        else:
            raise ValueError(f"Invalid collection type: {collection_type}")

    async def _batch_add_to_collection(
        self,
        collection_type: CollectionType,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        batch_size = 1000
        collection = self.collections[collection_type]

        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            logger.info(
                f"Adding batch {i // batch_size + 1} of {len(documents) // batch_size + 1} "
                f"to {collection_type.value} collection"
            )
            collection.add(
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end],
            )
