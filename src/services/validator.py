from typing import List

from core.prompts import prompts, PromptTemplate
from domain.chat import Message
from domain.validation import ValidationResult, ValidationStrategy
from interfaces.services.llm import LLMService
from interfaces.services.validator import QuestionValidatorService
from utils.format import format_knowledge_context, format_chat_history


class SmartStoreQuestionValidator(QuestionValidatorService):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def validate_question(
        self, query: str, chat_history: List[Message], similar_faqs: List[dict]
    ) -> ValidationResult:
        # 1단계: 직접적 관련성 검사
        direct_result = await self._execute_strategy(
            prompts.PT_DIRECT_VALIDATION,
            query,
            chat_history,
            similar_faqs,
            ValidationStrategy.DIRECT,
        )

        if direct_result.confidence > 0.7:
            return direct_result

        # 2단계: 간접적 관련성 검사
        indirect_result = await self._execute_strategy(
            prompts.PT_INDIRECT_VALIDATION,
            query,
            chat_history,
            similar_faqs,
            ValidationStrategy.INDIRECT,
        )

        if indirect_result.confidence > 0.5:
            return indirect_result

        # 3단계: 의도 분석
        intent_result = await self._execute_strategy(
            prompts.PT_INTENT_VALIDATION,
            query,
            chat_history,
            similar_faqs,
            ValidationStrategy.INTENT,
        )

        # 최종 판단
        results = [direct_result, indirect_result, intent_result]
        best_result = max(results, key=lambda x: x.confidence)

        return best_result

    async def _execute_strategy(
        self,
        prompt_template: PromptTemplate,
        query: str,
        chat_history: List[Message],
        similar_faqs: List[dict],
        strategy: ValidationStrategy,
    ) -> ValidationResult:
        messages = prompt_template.format(
            query=query,
            chat_history=format_chat_history(chat_history),
            context=format_knowledge_context(similar_faqs),
        )

        response = await self.llm_service.generate_completion(messages=messages)

        # 응답 파싱
        try:
            confidence = float(response.split(",")[1].strip())
            is_related = confidence > 0.5
            reasoning = (
                response.split(",")[2].strip() if len(response.split(",")) > 2 else ""
            )
        except:
            confidence = 0.0
            is_related = False
            reasoning = "Failed to parse response"

        return ValidationResult(
            is_related=is_related,
            confidence=confidence,
            strategy=strategy,
            reasoning=reasoning,
        )
