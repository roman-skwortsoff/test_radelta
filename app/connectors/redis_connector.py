import logging

import redis.asyncio as redis


logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        if self.redis is not None:
            return

        logger.info(f"async Начинаю подключение к Redis host={self.host}")

        self.redis = redis.Redis(host=self.host, port=self.port)

        try:
            await self.redis.ping()
            logger.info(f"async Успешное подключение к Redis host={self.host}")
        except ConnectionError as e:
            self.redis = None
            logger.error(f"async Не удалось подключиться к Redis: {e}")
            raise
        except Exception as e:
            self.redis = None
            logger.error(f"async Ошибка Redis: {e}")
            raise

    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
