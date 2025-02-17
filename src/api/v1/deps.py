from typing import Annotated

from fastapi import Depends, HTTPException, Header

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


async def get_session_id(x_session_id: str | None = Header(None)) -> str:
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    return x_session_id
