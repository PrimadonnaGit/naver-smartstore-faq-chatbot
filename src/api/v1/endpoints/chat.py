from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

from api.v1.deps import get_chat_service, get_session_id
from schemes.response import ChatRequest, ErrorResponse, WelcomeResponse
from services.chat import SmartStoreChatService
from utils.streaming import StreamingJsonResponse

router = APIRouter()


@router.post(
    "/",
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def chat(
    request: ChatRequest,
    chat_service: Annotated[SmartStoreChatService, Depends(get_chat_service)],
    session_id: Annotated[str, Depends(get_session_id)],
) -> StreamingResponse:
    """
    채팅 메시지를 처리하고 스트리밍 응답을 반환합니다.
    """
    try:
        response_generator = chat_service.process_message(
            session_id=session_id, message=request.message
        )

        return StreamingResponse(
            StreamingJsonResponse.create_stream(response_generator),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/welcome",
    response_model=WelcomeResponse,
    responses={
        200: {"description": "Welcome message with session ID"},
        500: {"model": ErrorResponse},
    },
)
async def welcome(
    chat_service: Annotated[SmartStoreChatService, Depends(get_chat_service)],
) -> WelcomeResponse:
    """웰컴 메시지와 새로운 세션 ID를 반환합니다."""
    try:
        response = await chat_service.get_welcome_message()
        session_id = str(uuid4())
        return WelcomeResponse(content=response.message, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
