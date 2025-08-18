from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel, NonNegativeInt

from app.database import async_session_maker
from app.utils.db_manager import DB_Manager
from app.setup import mongo_manager
from app.repositories.analytics import AnalyticsRepository


class PaginationParams(BaseModel):
    page: Annotated[NonNegativeInt, Query(default=1, ge=1)] = 1
    per_page: Annotated[NonNegativeInt | None, Query(default=None, ge=1, le=30)] = None


PaginationDep = Annotated[PaginationParams, Depends()]


def get_db_manager():
    return DB_Manager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DB_Manager, Depends(get_db)]


async def _get_mongo_repo(repo_class):
    db = await mongo_manager.get_mongodb()
    return repo_class(db)


async def get_analytics_repo():
    return await _get_mongo_repo(AnalyticsRepository)


MongoAnalyticsDep = Annotated[AnalyticsRepository, Depends(get_analytics_repo)]
