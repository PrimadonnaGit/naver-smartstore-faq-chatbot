import json
from typing import Any, AsyncGenerator

from domain.chat import ChatResponse


class StreamingJsonResponse:
    @staticmethod
    def format_sse(data: dict[str, Any]) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    async def create_stream(
        response_generator: AsyncGenerator[ChatResponse, None],
    ) -> AsyncGenerator[str, None]:
        async for response in response_generator:
            if response.message == "[DONE]":
                if response.follow_up:
                    yield StreamingJsonResponse.format_sse(
                        {"type": "follow_up", "content": response.follow_up}
                    )
                yield StreamingJsonResponse.format_sse(
                    {"type": "done", "content": "[DONE]"}
                )
            else:
                yield StreamingJsonResponse.format_sse(
                    {"type": "message", "content": response.message}
                )
