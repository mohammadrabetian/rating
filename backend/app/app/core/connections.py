from typing import Optional

from aioredis import Redis, create_redis_pool

from app.core.config import settings


class RedisCache:
    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self, db=0):
        self.redis_cache = await create_redis_pool(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", db=db
        )

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def execute(self, command, key, value, ex_command, ex_value, **kwargs):
        return await self.redis_cache.execute(
            command, key, value, ex_command, ex_value, **kwargs
        )

    async def close(self):
        self.redis_cache.close()
        await self.redis_cache.wait_closed()

    async def delete(self, key):
        await self.redis_cache.delete(key)


redis_cache = RedisCache()
