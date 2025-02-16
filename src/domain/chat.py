from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    content: str
    role: Literal["system", "user", "assistant"]


@dataclass
class ChatResponse:
    message: str
    follow_up: str | None = None
    metadata: dict | None = None
