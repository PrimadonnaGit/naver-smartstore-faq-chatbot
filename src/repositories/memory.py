import json

from core.config import settings
from core.decorators import log_execution_time
from domain.chat import Message
from infrastructure.redis.client import RedisClient
from interfaces.repositories.memory import ChatMemoryRepository


class RedisChatMemoryRepository(ChatMemoryRepository):
    def __init__(self, message_ttl: int = None):
        self.message_ttl = message_ttl or settings.REDIS_MESSAGE_TTL
        self.max_messages = 20

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

    @log_execution_time
    async def save_message(self, session_id: str, message: Message) -> None:
        async with RedisClient.get_connection() as redis:
            key = self._get_key(session_id)

            async with redis.pipeline() as pipe:
                await pipe.lpush(key, self._serialize_message(message))
                await pipe.ltrim(key, 0, self.max_messages - 1)
                await pipe.expire(key, self.message_ttl)
                await pipe.execute()

    @log_execution_time
    async def get_recent_messages(
        self, session_id: str, limit: int = 10
    ) -> list[Message]:
        async with RedisClient.get_connection() as redis:
            key = self._get_key(session_id)
            messages_json = await redis.lrange(key, 0, limit - 1)

            return [self._deserialize_message(msg_json) for msg_json in messages_json]
