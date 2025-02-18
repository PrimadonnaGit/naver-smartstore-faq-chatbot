from dataclasses import dataclass

from core.enums import CollectionType


@dataclass
class NaverFAQ:
    question: str
    answer: str
    tags: list[str]


@dataclass
class SearchResult:
    question: str
    answer: str
    score: float
    collection_type: CollectionType
