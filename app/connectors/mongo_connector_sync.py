import logging
from pymongo import MongoClient
from typing import Optional


logger = logging.getLogger(__name__)


class MongoManagerSync:
    def __init__(self, mongo_url: str, db_name: str, max_pool_size: int = 100):
        self._mongo_url = mongo_url
        self._db_name = db_name
        self._max_pool_size = max_pool_size
        self._client: Optional[MongoClient] = None
        self._db = None

    def connect(self) -> None:
        if self._client is None:
            self._client = MongoClient(
                self._mongo_url,
                maxPoolSize=self._max_pool_size,
                serverSelectionTimeoutMS=5000,  # таймаут подключения 5 сек
                connect=False,
            )
            self._db = self._client[self._db_name]
            try:
                self._db.command("ping")
                logger.info(f"✅ MongoDB connected to {self._db_name} (sync)")
            except Exception as e:
                self.close()
                logger.error("Ошибка подключения Mongo")
                raise ConnectionError(f"MongoDB connection failed: {e}")

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("🚪 MongoDB connection closed (sync)")

    def get_mongodb(self) -> MongoClient:
        if self._db is None:
            logger.info("Нет соединения с базой Mongo (connect=False), подключаемся")
            self.connect()
        return self._db
