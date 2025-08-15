from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.dependencies import DBDep, PaginationDep
from app.exceptions import DataBaseIntegrityException
from app.schemas.packages import PackageBrif, PackageCreate, PackageAddData, PackageRead
from app.schemas.reference import AddResponse
from app.tasks.tasks import set_delivery_costs, log_package_to_mongo
from app.config import settings


router = APIRouter(prefix="/packages", tags=["Посылки"])


@router.get(
    "/",
    summary="Получение информации о всех посылках",
    description="Возвращает список посылок с пагинацией. Можно фильтровать по типу и по наличию стоимости доставки.",
    response_model=List[PackageBrif],
    responses={
        200: {"description": "Список посылок успешно получен"},
        422: {"description": "Некорректные параметры запроса"},
    },
)
async def get_packages(
    db: DBDep,
    request: Request,
    pagination: PaginationDep,
    type_filter: Optional[str] = Query(
        None, description="Фильтр по типу посылки (id или часть названия)"
    ),
    has_delivery_cost: Optional[bool] = Query(
        None, description="Фильтр по расчету доставки."
    ),
):
    """
    Получение информации о всех посылках с фильтрацией и постраничной навигацией.

    - **type_filter**: фильтр по типу посылки (id или часть названия)
    - **has_delivery_cost**: фильтр по наличию стоимости доставки
    - **pagination**: параметры пагина"""

    per_page = pagination.per_page or 5
    session_id = request.cookies.get("session_id")
    return await db.packages.get_filtered_by_type(
        session_id=session_id,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        type_filter=type_filter,
        has_delivery_cost=has_delivery_cost,
    )


@router.post(
    "/",
    summary="Создать новую посылку",
    description="Создаёт новую посылку и возвращает её ID. Статус ответа 201 Created.",
    response_model=AddResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Посылка успешно создана"},
        409: {"description": "Ошибка в заполненных данных"},
    },
)
async def post_package(
    db: DBDep,
    request: Request,
    data: PackageCreate,
):
    session_id = request.cookies.get("session_id")
    package_data = PackageAddData(**data.model_dump(), session_id=session_id)

    try:
        result = await db.packages.add(package_data)
    except DataBaseIntegrityException:
        raise HTTPException(status_code=409, detail="Ошибка в заполненных данных")

    await db.commit()

    if settings.MODE != "TEST":
        log_package_to_mongo.delay(
            package_id=result["id"],
            type_id=data.type_id,
            weight_kg=str(data.weight_kg),
            value_usd=str(data.value_usd),
        )

    return result


@router.post(
    "/update",
    summary="Рассчитать стоимости доставок",
    description="Запускает фоновый расчёт стоимости доставок для всех посылок.",
    response_model=dict,
    responses={200: {"description": "Запрос на расчет стоимостей отправлен"}},
)
async def update_delivery_costs():
    set_delivery_costs.delay()
    return {"status": "Запрос на расчет стоимостей отправлен"}


@router.get(
    "/{package_id}",
    summary="Получение информации о конкретной посылке",
    description="Возвращает информацию о посылке по её ID.",
    response_model=PackageRead,
    responses={
        200: {"description": "Информация о посылке успешно получена"},
        404: {"description": "Посылка с указанным ID не найдена"},
    },
)
async def get_package(
    db: DBDep,
    request: Request,
    package_id: int,
):
    session_id = request.cookies.get("session_id")
    result = await db.packages.get_one(id=package_id, session_id=session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
    return result
