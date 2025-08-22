from app.connectors.mongo_connector import MongoManager
from app.connectors.mongo_connector_sync import MongoManagerSync
from app.connectors.redis_connector import RedisManager
from app.connectors.redis_connector_sync import RedisManagerSync
from app.config import settings


redis_manager = RedisManager(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

redis_manager_sync = RedisManagerSync(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT
)


mongo_manager = MongoManager(
    mongo_url=settings.MONGO_URL, db_name=settings.MONGODB_NAME
)

mongo_manager_sync = MongoManagerSync(
    mongo_url=settings.MONGO_URL, db_name=settings.MONGODB_NAME
)
