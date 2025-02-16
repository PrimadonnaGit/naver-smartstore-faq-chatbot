import json

from core.config import settings
from domain.chat import Message
from infrastructure.redis.client import RedisClient
from interfaces.repositories.memory import ChatMemoryRepository


class RedisChatMemoryRepository(ChatMemoryRepository):
    def __init__(self, message_ttl: int = None):
        self.message_ttl = message_ttl or settings.REDIS_MESSAGE_TTL

    def _get_key(self, session_id: str) -> str:
        return f"chat:memory:{session_id}"

    def _serialize_message(self, message: Message) -> str:
        return json.dumps(
            {
                "content": message.content,
                "role": message.role,
            }
        )

    def _deserialize_message(self, message_json: str) -> Message:
        data = json.loads(message_json)
        return Message(
            content=data["content"],
            role=data["role"],
        )

    async def save_message(self, session_id: str, message: Message) -> None:
        async with RedisClient.get_connection() as redis:
            key = self._get_key(session_id)

            async with redis.pipeline() as pipe:
                await pipe.lpush(key, self._serialize_message(message))
                await pipe.ltrim(key, 0, 99)  # 최근 100개 메시지만 유지
                await pipe.expire(key, self.message_ttl)
                await pipe.execute()

    async def get_recent_messages(
        self, session_id: str, limit: int = 10
    ) -> list[Message]:
        async with RedisClient.get_connection() as redis:
            key = self._get_key(session_id)
            messages_json = await redis.lrange(key, 0, limit - 1)

            return [
                self._deserialize_message(msg_json)
                for msg_json in reversed(messages_json)
            ]
