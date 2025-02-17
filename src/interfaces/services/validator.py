from abc import ABC, abstractmethod

from domain.chat import Message
from domain.validation import ValidationResult


class QuestionValidatorService(ABC):
    @abstractmethod
    async def validate_question(
        self, query: str, chat_history: list[Message], similar_faqs: list[dict]
    ) -> ValidationResult:
        pass
