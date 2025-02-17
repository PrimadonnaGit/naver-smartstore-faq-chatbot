from typing import Annotated

from fastapi import Depends, HTTPException, Header

from interfaces.repositories.knowledge import KnowledgeBaseRepository
from interfaces.repositories.memory import ChatMemoryRepository
from interfaces.services.llm import LLMService
from interfaces.services.validator import QuestionValidatorService
from repositories.knowledge import ChromaKnowledgeRepository
from repositories.memory import RedisChatMemoryRepository
from services.chat import SmartStoreChatService
from services.llm import OpenAIService
from services.validator import SmartStoreQuestionValidator


async def get_llm_service() -> LLMService:
    return OpenAIService()


async def get_validator_service(
    llm_service: LLMService = Depends(get_llm_service),
) -> QuestionValidatorService:
    return SmartStoreQuestionValidator(llm_service=llm_service)


async def get_memory_repository() -> ChatMemoryRepository:
    return RedisChatMemoryRepository()


async def get_knowledge_repository() -> KnowledgeBaseRepository:
    return ChromaKnowledgeRepository()


async def get_chat_service(
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
    validator_service: Annotated[
        QuestionValidatorService, Depends(get_validator_service)
    ],
    memory_repository: Annotated[ChatMemoryRepository, Depends(get_memory_repository)],
    knowledge_repository: Annotated[
        KnowledgeBaseRepository, Depends(get_knowledge_repository)
    ],
) -> SmartStoreChatService:
    return SmartStoreChatService(
        llm_service=llm_service,
        validator_service=validator_service,
        memory_repository=memory_repository,
        knowledge_repository=knowledge_repository,
    )


async def get_session_id(x_session_id: str | None = Header(None)) -> str:
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    return x_session_id
