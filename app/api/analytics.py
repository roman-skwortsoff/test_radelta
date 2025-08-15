import logging
from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime
from typing import List, Optional
from fastapi_cache.decorator import cache

from app.api.dependencies import MongoAnalyticsDep
from app.exceptions import InvalidDateRangeError, TypeIdNotFoundError


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/analytics", tags=["Analytics Analytics"])


@cache(expire=60 * 10)
@router.get(
    "/daily_totals",
    summary="Получить суммы доставок за день",
    description="Возвращает суммы доставок и количество посылок по каждому типу за конкретную дату.",
    responses={
        200: {"description": "Успешный ответ"},
    },
)
async def get_daily_delivery_totals(
    db: MongoAnalyticsDep,
    day: str = Query(default=date.today(), description="Дата в формате YYYY-MM-DD"),
) -> List[dict]:
    """
    Считает сумму доставок по типам за конкретный день.

    - **day**: дата, за которую нужно получить данные.
    - Возвращает список словарей, где:
        - **type_id** — ID типа доставки
        - **total_delivery_cost_rub** — общая стоимость в рублях
        - **count_packages** — количество посылок
    """
    return await db.get_daily_totals(day)


@router.get(
    "/delivery_totals_range",
    summary="Получить агрегированную статистику доставок",
    response_model=List[dict],
    description="""
Возвращает общую стоимость доставки и количество посылок
за указанный диапазон дат, с возможной фильтрацией по `type_id`.
- Даты должны быть в формате **YYYY-MM-DD**.
- Если `type_id` указан, но не найден — будет ошибка 404.
- Если дата начала позже даты конца — будет ошибка 400.
    """,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Неверный диапазон дат"},
        404: {"description": "type_id не найден"},
        422: {"description": "Ошибка валидации параметров"},
    },
)
async def delivery_totals_range(
    db: MongoAnalyticsDep,
    start_date: date = Query(..., description="Дата начала в формате YYYY-MM-DD"),
    end_date: date = Query(..., description="Дата конца в формате YYYY-MM-DD"),
    type_id: Optional[int] = Query(None, description="Фильтр по type_id, опциональный"),
):
    """
    Получить агрегированную статистику доставок по диапазону дат.
    """
    try:
        results = await db.get_totals_range(start_date, end_date, type_id)
        return [
            {
                "type_id": r["_id"],
                "total_delivery_cost_rub": round(r["total_delivery_cost"], 2),
                "count_packages": r["count_packages"],
            }
            for r in results
        ]
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=400, detail=e.detail)
    except TypeIdNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")


@router.get(
    "/all",
    response_model=List[dict],
    summary="Получить все логи доставок",
    description="Возвращает список логов доставок с фильтрацией, сортировкой и пагинацией. Используется для отладки.",
    responses={
        200: {"description": "Успешный ответ"},
    },
)
async def get_all_delivery_logs(
    db: MongoAnalyticsDep,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска (skip)"),
    limit: int = Query(
        100, le=1000, description="Максимальное количество записей (limit)"
    ),
    type_id: Optional[int] = Query(None, description="Фильтр по типу посылки"),
    date_from: Optional[datetime] = Query(
        None, description="Начальная дата фильтрации"
    ),
    date_to: Optional[datetime] = Query(None, description="Конечная дата фильтрации"),
    sort_field: str = Query(
        "created_at",
        description="Поле для сортировки (например, created_at, package_id)",
    ),
    sort_order: str = Query(
        "desc", regex="^(asc|desc)$", description="Порядок сортировки: asc или desc"
    ),
) -> List[dict]:
    """
    Для отладки - получение всех логов доставок с пагинацией

    Параметры:
    - skip: Пропустить первые N записей
    - limit: Максимальное количество записей (макс. 1000)
    - type_id: Фильтр по типу посылки
    - date_from: Начальная дата для фильтрации
    - date_to: Конечная дата для фильтрации
    - sort_field: Поле для сортировки (created_at, package_id и т.д.)
    - sort_order: Порядок сортировки (asc/desc)
    """

    return await db.get_all(
        skip=skip,
        limit=limit,
        type_id=type_id,
        date_from=date_from,
        date_to=date_to,
        sort_field=sort_field,
        sort_order=sort_order,
    )
