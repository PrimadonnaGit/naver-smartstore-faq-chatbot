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
    SMARTSTORE_CHECK = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 관련 질문을 분류하는 전문가입니다. 주어진 질문이 스마트스토어와 관련이 있는지 true 또는 false로만 답변해주세요.",
            ),
            Message(role="user", content="질문: {query}"),
        ]
    )

    CHAT_RESPONSE = PromptTemplate(
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

    FOLLOW_UP = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 고객 지원 전문가입니다. 이전 질의응답을 바탕으로 사용자가 추가로 궁금해할 만한 자연스러운 후속 질문 하나를 생성해주세요.",
            ),
            Message(role="user", content="이전 질문: {query}"),
            Message(role="assistant", content="{answer}"),
            Message(
                role="system",
                content="위 대화를 바탕으로 사용자가 추가로 궁금해할 만한 자연스러운 후속 질문을 하나만 생성해주세요.",
            ),
        ]
    )

    CONTEXTUAL_RESPONSE = PromptTemplate(
        [
            Message(
                role="system",
                content="""당신은 네이버 스마트스토어 고객 지원 전문가입니다. 
FAQ 데이터를 참고하여 친절하고 전문적으로 답변해주세요.

답변시 유의사항:
1. FAQ의 내용을 기반으로 하되, 자연스럽게 답변해주세요.
2. 이전 대화 맥락을 고려해주세요.
3. 모든 중요한 정보를 포함해주세요.
4. 전문 용어는 쉽게 설명해주세요.""",
            ),
            Message(role="system", content="참고할 FAQ 정보:\n{similar_qa}"),
        ]
    )


prompts = PromptTemplates()
