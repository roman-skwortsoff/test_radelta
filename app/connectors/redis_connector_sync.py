import logging
import redis

logger = logging.getLogger(__name__)


class RedisManagerSync:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    def connect(self):
        logger.info(f"Начинаю подключение к Redis host={self.host}")

        if self.redis is not None:
            return

        self.redis = redis.Redis(host=self.host, port=self.port)

        try:
            self.redis.ping()
            logger.info(f"Успешное подключение к Redis host={self.host}")
        except ConnectionError as e:
            self.redis = None
            logger.error(f"Не удалось подключиться к Redis: {e}")
            raise
        except Exception as e:
            self.redis = None
            logger.error(f"Ошибка Redis: {e}")
            raise

    def set(self, key: str, value: str, expire: int = None):
        if expire:
            self.redis.set(key, value, ex=expire)
        else:
            self.redis.set(key, value)

    def get(self, key: str):
        return self.redis.get(key)

    def delete(self, key: str):
        self.redis.delete(key)

    def close(self):
        if self.redis:
            self.redis.close()
