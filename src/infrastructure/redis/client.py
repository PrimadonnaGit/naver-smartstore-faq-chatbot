from contextlib import asynccontextmanager

from redis.asyncio import Redis, ConnectionPool

from core.config import settings


class RedisClient:
    _pool: ConnectionPool = None

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        if cls._pool is None:
            cls._pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
        return cls._pool

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        async with Redis(connection_pool=cls.get_pool()) as redis:
            yield redis
