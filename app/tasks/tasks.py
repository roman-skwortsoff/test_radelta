from datetime import datetime
import logging
from decimal import Decimal
from typing import Optional
from zoneinfo import ZoneInfo
from asgiref.sync import async_to_sync

from app.tasks.celery_app import celery_instance
from app.tasks.task_helpers import get_usd_rate, update_usd_rate_from_cbr
from app.database import async_session_maker_null
from app.utils.db_manager import DB_Manager
from app.setup import mongo_manager_sync


logger = logging.getLogger(__name__)

BATCH_SIZE = 100
buffer: list[dict] = []


def push_buffer():
    """Записываем буфер в MongoDB и очищаем"""
    if not buffer:
        logger.debug("Буфер пустой")
        return
    db = mongo_manager_sync.get_mongodb()
    try:
        db.delivery_logs.insert_many(buffer)
        logger.debug(f"Записано в Mongo {len(buffer)} записей")
        buffer.clear()
    except Exception as e:
        logger.error(f"Ошибка батчевой записи в Mongo: {e}")


@celery_instance.task(name="insert_buffer_to_mongo")
def insert_buffer_to_mongo():
    """Периодическая запись буфера в Mongo"""
    push_buffer()


@celery_instance.task(name="add_to_mongo")
def log_package_to_mongo(package_id, type_id, weight_kg, value_usd):
    try:
        usd_rub_rate = get_usd_rate()
        is_estimated = False

        if usd_rub_rate is None:
            last_rate = get_last_saved_rate()
            if last_rate is None:
                logger.error("Нет доступного курса USD — отмена записи")
                return
            logger.warning(f"Используем последний известный курс: {last_rate}")
            usd_rub_rate = last_rate
            is_estimated = True

        now = datetime.now(ZoneInfo("Europe/Moscow"))
        document = {
            "package_id": package_id,
            "type_id": type_id,
            "weight_kg": float(weight_kg),
            "value_usd": float(value_usd),
            "usd_rub_rate": float(usd_rub_rate),
            "is_estimated": is_estimated,
            "created_at": now,
            "day_key": now.strftime("%Y-%m-%d"),
            "hour": now.hour,
        }

        buffer.append(document)

        if len(buffer) >= BATCH_SIZE:
            push_buffer()

    except Exception as e:
        logger.error(f"Ошибка записи package_id={package_id}: {str(e)}")


def get_last_saved_rate() -> Optional[float]:
    """Возвращает последний сохранённый курс из MongoDB"""
    db = mongo_manager_sync.get_mongodb()
    last_entry = db.delivery_logs.find_one(
        {"usd_rub_rate": {"$exists": True}}, sort=[("created_at", -1)]
    )
    return last_entry["usd_rub_rate"] if last_entry else None


@celery_instance.task(name="set_usd_course")
def set_usd_course():
    update_usd_rate_from_cbr()


async def _update_delivery_costs_async(usd_rub_rate: Decimal):
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        updated_count = await db.packages.update_costs(usd_rub_rate)
        if updated_count > 0:
            await db.commit()
        logger.info(f"Обновлено стоимостей доставок: {updated_count}")


@celery_instance.task(name="set_delivery_costs")
def set_delivery_costs():
    usd_rub_rate = get_usd_rate()
    if usd_rub_rate is None:
        logger.warning("Нет курса USD — обновление стоимостей отменено")
        return
    async_to_sync(_update_delivery_costs_async)(usd_rub_rate)
