import logging
from decimal import Decimal
import httpx

from app.setup import redis_manager_sync


logger = logging.getLogger(__name__)


def ensure_redis_connection():
    """Гарантирует, что Redis подключён"""
    try:
        redis_manager_sync.redis.ping()
    except Exception:
        logger.warning("Redis соединение потеряно. Переподключаемся...")
        redis_manager_sync.connect()


def get_usd_rate() -> Decimal | None:
    """Возвращает курс USD из Redis или None"""
    ensure_redis_connection()
    raw = redis_manager_sync.get("USD_RUB")
    if raw is None:
        return
    return Decimal(raw.decode())


def update_usd_rate_from_cbr() -> Decimal | None:
    """Запрашивает курс USD с ЦБ и пишет в Redis"""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        rate = Decimal(str(data["Valute"]["USD"]["Value"]))

        redis_manager_sync.set("USD_RUB", str(rate), expire=120 * 60)
        logger.info(f"Курс USD_RUB обновлен: {rate}")
        return rate
    except Exception as e:
        logger.error(f"Ошибка при получении курса USD: {e}")
        return
