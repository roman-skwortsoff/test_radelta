from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class MongoManager:
    def __init__(self, mongo_url: str, db_name: str, max_pool_size: int = 100):
        self._mongo_url = mongo_url
        self._db_name = db_name
        self._max_pool_size = max_pool_size
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(
                self._mongo_url,
                maxPoolSize=self._max_pool_size,
                serverSelectionTimeoutMS=5000,  # Таймаут подключения 5 сек
                connect=False,
            )
            self._db = self._client[self._db_name]
            try:
                await self._db.command("ping")
                logger.info(f"✅ MongoDB connected to {self._db_name}")
            except Exception as e:
                await self.close()
                logger.error("Ошибка подключения Mongo")
                raise ConnectionError(f"MongoDB connection failed: {e}")

    async def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("🚪 MongoDB connection closed")

    async def get_mongodb(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            logger.info("Нет соединения с базой Mongo (connect=False), подключаемся")
            await self.connect()
        try:
            return self._db
        except Exception as e:
            logger.error(f"⚠️ MongoDB error: {e}")
            raise

    async def aggregate(self, collection: str, pipeline: list) -> list:
        """Универсальный метод агрегации"""
        db = await self.get_mongodb()
        cursor = db[collection].aggregate(pipeline)
        return await cursor.to_list(length=10000)
