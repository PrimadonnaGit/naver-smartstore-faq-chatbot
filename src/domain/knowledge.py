from dataclasses import dataclass


@dataclass
class FAQ:
    question: str
    answer: str
    tags: list[str]
