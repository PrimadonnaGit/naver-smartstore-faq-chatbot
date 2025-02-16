from fastapi import APIRouter

from api.v1.endpoints import chat

api_v1_router = APIRouter()
api_v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])
