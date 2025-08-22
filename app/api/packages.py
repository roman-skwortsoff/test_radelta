from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import Field

from app.api.dependencies import DBDep, PaginationDep
from app.exceptions import DataBaseIntegrityException, ObjectNotFoundException
from app.schemas.packages import PackageBrief, PackageCreate, PackageAddData, PackageRead
from app.schemas.reference import AddResponse
from app.tasks.tasks import set_delivery_costs, log_package_to_mongo
from app.config import settings


router = APIRouter(prefix="/packages", tags=["Посылки"])

DEFAULT_PER_PAGE = 10


@router.get(
    "/",
    summary="Получение информации о всех посылках",
    description="Возвращает список посылок с пагинацией. Можно фильтровать по типу и по наличию стоимости доставки.",
    response_model=List[PackageBrief],
    responses={
        200: {"description": "Список посылок успешно получен"},
        422: {"description": "Некорректные параметры запроса"},
    },
)
async def get_packages(
    db: DBDep,  # type: ignore
    request: Request,
    pagination: PaginationDep,  # type: ignore
    type_filter: Annotated[
        str | None,
        Query(description="Фильтр по типу посылки", min_length=1, max_length=50),
    ] = None,
    has_delivery_cost: Annotated[
        bool | None, Query(description="Фильтр по расчету доставки")
    ] = None,
):
    """
    Получение информации о всех посылках с фильтрацией и постраничной навигацией.

    - **type_filter**: фильтр по типу посылки (id или часть названия)
    - **has_delivery_cost**: фильтр по наличию стоимости доставки
    - **pagination**: параметры пагина"""

    per_page = pagination.per_page or DEFAULT_PER_PAGE
    return await db.packages.get_filtered_by_type(
        session_id=request.state.session_id,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        type_filter=type_filter,
        has_delivery_cost=has_delivery_cost,
    )


@router.post(
    "/",
    summary="Создать новую посылку",
    description="Создаёт новую посылку и возвращает её ID",
    response_model=AddResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Посылка успешно создана"},
        409: {"description": "Ошибка в заполненных данных"},
    },
)
async def post_package(
    db: DBDep,  # type: ignore
    request: Request,
    data: PackageCreate,
):
    package_data = PackageAddData(
        **data.model_dump(), session_id=request.state.session_id
    )

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

    return AddResponse(id=result["id"])


@router.post(
    "/update",
    summary="Рассчитать стоимости доставок",
    description="Запускает фоновый расчёт стоимости доставок для всех посылок.",
    response_model=dict[str, str],
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
    db: DBDep,  # type: ignore
    request: Request,
    package_id: Annotated[int, Field(..., ge=1, description="ID посылки")],
):
    try:
        return await db.packages.get_one(
            id=package_id, session_id=request.state.session_id
        )
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
