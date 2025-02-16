from typing import AsyncGenerator

from core.constants import WELCOME_MESSAGE, NO_SMARTSTORE_MESSAGE, UNRECOGNIZED_MESSAGE
from core.prompts import prompts
from domain.chat import Message, ChatResponse
from interfaces.repositories.knowledge import KnowledgeBaseRepository
from interfaces.repositories.memory import ChatMemoryRepository
from interfaces.services.chat import ChatService
from interfaces.services.llm import LLMService


class SmartStoreChatService(ChatService):
    def __init__(
        self,
        llm_service: LLMService,
        memory_repository: ChatMemoryRepository,
        knowledge_repository: KnowledgeBaseRepository,
    ):
        self.llm_service = llm_service
        self.memory_repository = memory_repository
        self.knowledge_repository = knowledge_repository

    def _format_chat_history(self, messages: list[Message]) -> str:
        if not messages:
            return ""
        return "\n".join(
            [f"{msg.role.capitalize()}: {msg.content}" for msg in messages]
        )

    def _format_knowledge_context(self, faqs: list[dict]) -> str:
        return "\n\n".join(
            [f"Q: {faq["question"]}\nA: {faq["answer"]}" for faq in faqs]
        )

    async def create_chat_completion(
        self,
        query: str,
        chat_history: list[Message],
        knowledge_context: str,
    ) -> AsyncGenerator[str, None]:
        messages = prompts.CHAT_RESPONSE.format(
            query=query,
            chat_history=self._format_chat_history(chat_history),
            context=knowledge_context,
        )

        async for chunk in await self.llm_service.generate_completion(
            messages=messages, stream=True
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def process_message(
        self, session_id: str, message: str
    ) -> AsyncGenerator[ChatResponse, None]:
        # 스마트스토어 관련 질문인지 확인
        is_related = await self.is_smartstore_related(message)
        if not is_related:
            yield ChatResponse(message=NO_SMARTSTORE_MESSAGE)
            return

        # 사용자 메시지 저장
        user_message = Message(content=message, role="user")
        await self.memory_repository.save_message(session_id, user_message)

        # 이전 대화 내역 조회
        chat_history = await self.memory_repository.get_recent_messages(
            session_id, limit=5
        )

        # 관련 FAQ 검색
        similar_faqs = await self.knowledge_repository.find_similar(message)
        if not similar_faqs:
            yield ChatResponse(message=UNRECOGNIZED_MESSAGE)
            return

        # 답변 생성 및 스트리밍
        answer_chunks = []
        async for chunk in self.create_chat_completion(
            query=message,
            chat_history=chat_history,
            knowledge_context=self._format_knowledge_context(similar_faqs),
        ):
            answer_chunks.append(chunk)
            yield ChatResponse(message=chunk)

        # 완성된 답변 저장
        complete_answer = "".join(answer_chunks)
        assistant_message = Message(content=complete_answer, role="assistant")
        await self.memory_repository.save_message(session_id, assistant_message)

        # 후속 질문 생성
        yield await self.get_follow_up_message(message, complete_answer)

    async def get_follow_up_message(self, query: str, answer: str) -> ChatResponse:
        messages = prompts.FOLLOW_UP.format(query=query, answer=answer)
        follow_up = await self.llm_service.generate_completion(
            messages=messages, temperature=0.7
        )
        return ChatResponse(message="[DONE]", follow_up=follow_up)

    async def is_smartstore_related(self, query: str) -> bool:

        messages = prompts.SMARTSTORE_CHECK.format(query=query)
        response = await self.llm_service.generate_completion(
            messages=messages, temperature=0.1
        )
        return response.strip().lower() == "true"

    async def get_welcome_message(self) -> ChatResponse:
        return ChatResponse(message=WELCOME_MESSAGE)
