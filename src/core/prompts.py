from typing import Any

from domain.chat import Message


class PromptTemplate:
    def __init__(self, messages: list[Message]):
        self.messages = messages

    def format(self, **kwargs: Any) -> list[dict[str, str]]:
        return [
            {"role": msg.role, "content": msg.content.format(**kwargs)}
            for msg in self.messages
        ]


class PromptTemplates:
    PT_QUESTION_VALIDATION_CHECK = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 관련 질문을 분류하는 전문가입니다. 주어진 질문이 스마트스토어와 관련이 있는지 true 또는 false로만 답변해주세요.",
            ),
            Message(role="user", content="질문: {query}"),
        ]
    )

    PT_FAQ_QUESTION = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 고객 지원 전문가입니다.\n"
                "다음 FAQ를 참고하여 자연스럽고 친절하게 답변해주세요:\n\n"
                "{context}\n\n"
                "이전 대화:\n{chat_history}",
            ),
            Message(role="user", content="{query}"),
        ]
    )

    PT_FOLLOW_UP_QUESTIONS = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 고객 지원 전문가입니다.\n"
                "이전 질의응답을 바탕으로 사용자가 추가로 궁금해할 만한 자연스러운 후속 질문 2개 생성해주세요.\n"
                "각 질문은 새로운 줄에 작성해주세요.",
            ),
            Message(role="assistant", content="이전 질문: {query}"),
            Message(role="assistant", content="{answer}"),
        ]
    )


prompts = PromptTemplates()
