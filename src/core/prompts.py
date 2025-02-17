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
                content="당신은 네이버 스마트스토어 관련 질문을 분류하는 전문가입니다.\n"
                "다음의 기준으로 질문을 평가해주세요:\n"
                "- 스마트스토어 회원가입, 상품관리, 쇼핑윈도에관리 관한 질문\n"
                "- 스마트스토어 판매관리, 정산관리, 문의/리뷰관리, 스토어관리, 혜택/마케팅에 관한 질문\n"
                "- 스마트스토어 브랜드 혜택/마케팅, 커머스솔루션, 통계, 광고관리, 프로모션 관리에 관한 질문\n"
                "- 스마트스토어 물류 관리, 판매자 정보 등에 관한 질문\n"
                "- 위 내용이 포함되지 않더라도 스마트스토어 이용에 관련이 있을 수 있는 질문\n"
                "- 사용자의 이전 질문을 고려해 판단해주세요.\n"
                "주어진 질문이 위 기준에 부합하는지 true 또는 false로만 답변해주세요.\n\n"
                "이전 대화 기록:\n{chat_history}",
            ),
            Message(role="user", content="질문: {query}"),
        ]
    )

    PT_FAQ_QUESTION = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 고객 지원 전문가입니다.\n"
                "아래 지침을 따라 답변해주세요:\n\n"
                "1. 제공된 FAQ 내용을 기반으로 답변하되, 이전 대화 맥락을 고려하여 일관성 있게 답변하세요.\n"
                "2. 답변에 확신이 없는 내용은 포함하지 마세요.\n"
                "3. 사용자의 이전 질문과 현재 상황을 고려하여 맥락에 맞는 답변을 제공하세요.\n"
                "4. 전문 용어는 쉽게 풀어서 설명하세요.\n\n"
                "참고할 FAQ:\n{context}\n\n"
                "이전 대화 기록:\n{chat_history}",
            ),
            Message(role="user", content="{query}"),
        ]
    )

    PT_FOLLOW_UP_QUESTIONS = PromptTemplate(
        [
            Message(
                role="system",
                content="당신은 네이버 스마트스토어 고객 지원 전문가입니다.\n"
                "주어진 FAQ 내용과 이전 대화를 참고하여, 다음 기준에 따라 후속 질문을 개행 문자로 구분하여 최대 2개까지 생성해주세요:\n\n"
                "1. FAQ에서 답변 가능한 범위의 질문만 생성\n"
                "2. 이전 질문과 답변의 맥락을 고려한 자연스러운 후속 질문\n"
                "3. 스마트스토어와 관련 없는 질문의 경우:\n"
                "   - 현재 질문의 주제나 키워드를 스마트스토어와 연관 지어 질문 생성\n"
                "   - 예시: 음식점 추천 → '음식 관련 스마트스토어 등록에 관심이 있으신가요?'\n\n"
                "참고할 FAQ:\n{context}\n\n"
                "이전 대화 기록:\n{chat_history}",
            ),
            Message(role="assistant", content="현재 질문: {query}"),
            Message(role="assistant", content="현재 답변: {answer}"),
        ]
    )


prompts = PromptTemplates()
