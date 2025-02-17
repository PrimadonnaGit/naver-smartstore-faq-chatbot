from dataclasses import dataclass
from enum import Enum


class ValidationStrategy(Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    INTENT = "intent"


@dataclass
class ValidationResult:
    is_related: bool
    confidence: float
    strategy: ValidationStrategy
    reasoning: str
