from typing import Annotated
from uuid import uuid4

from fastapi import Depends

from repositories.knowledge import ChromaKnowledgeRepository
from repositories.memory import RedisChatMemoryRepository
from services.chat import SmartStoreChatService
from services.llm import OpenAIService


async def get_llm_service() -> OpenAIService:
    return OpenAIService()


async def get_memory_repository() -> RedisChatMemoryRepository:
    return RedisChatMemoryRepository()


async def get_knowledge_repository() -> ChromaKnowledgeRepository:
    return ChromaKnowledgeRepository()


async def get_chat_service(
    llm_service: Annotated[OpenAIService, Depends(get_llm_service)],
    memory_repository: Annotated[
        RedisChatMemoryRepository, Depends(get_memory_repository)
    ],
    knowledge_repository: Annotated[
        ChromaKnowledgeRepository, Depends(get_knowledge_repository)
    ],
) -> SmartStoreChatService:
    return SmartStoreChatService(
        llm_service=llm_service,
        memory_repository=memory_repository,
        knowledge_repository=knowledge_repository,
    )


def get_session_id(session_id: str | None = None) -> str:
    return session_id or str(uuid4())
