from dataclasses import dataclass


@dataclass
class FAQ:
    question: str
    answer: str
    clean_question: str
    tags: list[str]
