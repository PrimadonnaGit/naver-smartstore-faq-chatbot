import asyncio

from core.decorators import log_execution_time
from core.prompts import prompts, PromptTemplate
from domain.chat import Message
from domain.validation import ValidationResult, ValidationStrategy
from interfaces.services.llm import LLMService
from interfaces.services.validator import QuestionValidatorService
from utils.format import format_knowledge_context, format_chat_history


class SmartStoreQuestionValidator(QuestionValidatorService):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    @log_execution_time
    async def validate_question(
        self, query: str, chat_history: list[Message], similar_faqs: list[dict]
    ) -> ValidationResult:
        validation_tasks = [
            self._execute_strategy(
                prompts.PT_DIRECT_VALIDATION,
                query,
                chat_history,
                similar_faqs,
                ValidationStrategy.DIRECT,
            ),
            self._execute_strategy(
                prompts.PT_INDIRECT_VALIDATION,
                query,
                chat_history,
                similar_faqs,
                ValidationStrategy.INDIRECT,
            ),
        ]

        results = await asyncio.gather(*validation_tasks)

        # 가중치를 적용한 최종 점수 계산
        weighted_results = []
        for result in results:
            weighted_confidence = result.confidence * result.strategy.weight
            weighted_results.append(
                ValidationResult(
                    is_related=result.is_related,
                    confidence=weighted_confidence,
                    strategy=result.strategy,
                )
            )

        # 가중치가 적용된 결과 중 최고 점수 선택
        best_result = max(weighted_results, key=lambda x: x.confidence)

        # 최종 결과의 is_related 재계산 (가중치 적용 후)
        best_result.is_related = best_result.confidence > 0.5
        return best_result

    async def _execute_strategy(
        self,
        prompt_template: PromptTemplate,
        query: str,
        chat_history: list[Message],
        similar_faqs: list[dict],
        strategy: ValidationStrategy,
    ) -> ValidationResult:
        messages = prompt_template.format(
            query=query,
            chat_history=format_chat_history(chat_history),
            context=format_knowledge_context(similar_faqs),
        )

        response = await self.llm_service.generate_completion(messages=messages)

        try:
            confidence = float(response.split(",")[1].strip())
            is_related = confidence > 0.5
        except Exception as e:
            confidence = 0.0
            is_related = False

        return ValidationResult(
            is_related=is_related,
            confidence=confidence,
            strategy=strategy,
        )
