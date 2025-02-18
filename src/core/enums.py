from enum import Enum


class CollectionType(Enum):
    FULL = "full"
    QUESTION = "question"
    ANSWER = "answer"


class ValidationStrategy(Enum):
    DIRECT = ("direct", 1.0)
    INDIRECT = ("indirect", 0.8)

    def __init__(self, value: str, weight: float):
        self._value_ = value
        self.weight = weight
