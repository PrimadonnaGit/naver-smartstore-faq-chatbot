from dataclasses import dataclass

from core.enums import ValidationStrategy


@dataclass
class ValidationResult:
    is_related: bool
    confidence: float
    strategy: ValidationStrategy
