from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str | None = Field(default=None)


class ChatResponse(BaseModel):
    content: str
    type: str | None = "message"


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


class WelcomeResponse(BaseModel):
    content: str
    session_id: str
