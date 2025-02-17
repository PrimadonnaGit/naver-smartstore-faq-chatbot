from typing import AsyncGenerator

from core.constants import WELCOME_MESSAGE, NO_SMARTSTORE_MESSAGE, UNRECOGNIZED_MESSAGE
from core.logging import setup_logger
from core.prompts import prompts
from domain.chat import Message, ChatResponse
from interfaces.repositories.knowledge import KnowledgeBaseRepository
from interfaces.repositories.memory import ChatMemoryRepository
from interfaces.services.chat import ChatService
from interfaces.services.llm import LLMService

logger = setup_logger(__name__)


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
            [f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faqs]
        )

    async def create_chat_completion(
        self,
        query: str,
        chat_history: list[Message],
        knowledge_context: str,
    ) -> AsyncGenerator[str, None]:
        messages = prompts.PT_FAQ_QUESTION.format(
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
        # 이전 대화 내역 조회
        chat_history = await self.memory_repository.get_recent_messages(
            session_id, limit=10
        )

        # 관련 FAQ 검색
        similar_faqs = await self.knowledge_repository.find_similar(message, limit=10)

        # 사용자 메시지 저장
        user_message = Message(content=message, role="user")
        await self.memory_repository.save_message(session_id, user_message)

        # 스마트스토어 관련 질문인지 확인
        is_related = await self.is_smartstore_related(
            message, chat_history, similar_faqs
        )
        if not is_related:
            yield ChatResponse(message=NO_SMARTSTORE_MESSAGE)
            # 스마트스토어와 관련없는 질문이더라도 후속 질문은 생성
            yield await self.get_follow_up_message(
                query=message,
                answer="",
                chat_history=chat_history,
                similar_faqs=similar_faqs[:3],
            )
            return

        if not similar_faqs:
            yield ChatResponse(message=UNRECOGNIZED_MESSAGE)
            return

        # 답변 생성 및 스트리밍
        answer_chunks = []
        knowledge_context = self._format_knowledge_context(similar_faqs)

        async for chunk in self.create_chat_completion(
            query=message,
            chat_history=chat_history,
            knowledge_context=knowledge_context,
        ):
            answer_chunks.append(chunk)
            yield ChatResponse(message=chunk)

        # 완성된 답변 저장
        complete_answer = "".join(answer_chunks)
        assistant_message = Message(content=complete_answer, role="assistant")
        await self.memory_repository.save_message(session_id, assistant_message)

        # 후속 질문 생성
        yield await self.get_follow_up_message(
            query=message,
            answer=complete_answer,
            chat_history=chat_history,
            similar_faqs=similar_faqs[:3],
        )

    async def get_follow_up_message(
        self,
        query: str,
        answer: str,
        chat_history: list[Message],
        similar_faqs: list[dict],
    ) -> ChatResponse:
        follow_up_messages = prompts.PT_FOLLOW_UP_QUESTIONS.format(
            query=query,
            answer=answer,
            context=self._format_knowledge_context(similar_faqs),
            chat_history=self._format_chat_history(chat_history),
        )

        follow_up_response = await self.llm_service.generate_completion(
            messages=follow_up_messages, temperature=0.7
        )

        follow_ups = [q.strip() for q in follow_up_response.split("\n") if q.strip()][
            :2
        ]
        return ChatResponse(message="[DONE]", follow_ups=follow_ups)

    async def is_smartstore_related(
        self, query: str, chat_history: list[Message], similar_faqs: list[dict]
    ) -> bool:
        messages = prompts.PT_QUESTION_VALIDATION_CHECK.format(
            query=query,
            chat_history=self._format_chat_history(chat_history),
            context=similar_faqs,
        )
        response = await self.llm_service.generate_completion(
            messages=messages, temperature=0.1
        )

        is_related, confidence = response.strip().split(",")

        return is_related == "true" if float(confidence) > 0.5 else True

    async def get_welcome_message(self) -> ChatResponse:
        return ChatResponse(message=WELCOME_MESSAGE)
