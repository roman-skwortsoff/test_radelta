from typing import List
from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import DBDep
from app.exceptions import DataBaseIntegrityException, ObjectAlreadyExistException
from app.schemas.package_types import PackageTypeBase, PackageTypeRead
from app.schemas.reference import AddResponse


router = APIRouter(prefix="/package_types", tags=["Типы посылок"])


@router.get(
    "/",
    summary="Получение информации о всех типах посылок",
    response_model=List[PackageTypeRead],
    responses={
        200: {"description": "Список типов посылок"},
    },
)
async def get_package_types(
    db: DBDep,
):
    """
    Возвращает список всех типов посылок.
    Если в базе нет типов, возвращается пустой список.
    """
    return await db.package_types.get_all()


@router.post(
    "/",
    summary="Создать новый тип посылок",
    status_code=status.HTTP_201_CREATED,
    response_model=AddResponse,
    responses={
        201: {"description": "Тип посылки успешно создан"},
        409: {"description": "Конфликт данных (уже существует или ошибка целостности)"},
    },
)
async def post_package_type(
    db: DBDep,
    data: PackageTypeBase,
):
    """
    Создает новый тип посылки.

    Возможные ошибки:
    - **409 Conflict** — тип уже существует
    - **409 Conflict** — ошибка в данных (нарушение целостности)
    """
    try:
        result = await db.package_types.add(data)
    except ObjectAlreadyExistException:
        raise HTTPException(status_code=409, detail="Данный тип посылок уже существует")
    except DataBaseIntegrityException:
        raise HTTPException(status_code=409, detail="Ошибка в данных")
    await db.commit()
    return result
