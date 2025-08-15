# ruff: noqa: E402
from unittest import mock
import aiomysql

from app.schemas.package_types import PackageTypeBase

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest
from httpx import AsyncClient, ASGITransport

from app.api.dependencies import get_db
from app.config import settings
from app.database import Base, engine_null, async_session_maker_null
from app.main import app
from app.models import *  # noqa

from app.setup import redis_manager
from app.utils.db_manager import DB_Manager


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"

    root_user = "root"
    root_password = settings.ROOT_DB_PASS
    host = settings.DB_HOST
    port = settings.DB_PORT

    db_name = settings.DB_NAME
    test_user = settings.DB_USER
    test_password = settings.DB_PASS

    conn = await aiomysql.connect(
        host=host, port=port, user=root_user, password=root_password, autocommit=True
    )
    async with conn.cursor() as cur:
        await cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_name} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        await cur.execute(
            f"CREATE USER IF NOT EXISTS '{test_user}'@'%' IDENTIFIED BY '{test_password}';"
        )
        await cur.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{test_user}'@'%';")
        await cur.execute("FLUSH PRIVILEGES;")
        conn.close()

    async with engine_null.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db_null():
    await redis_manager.connect()
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        yield db
    await redis_manager.close()


app.dependency_overrides[get_db] = get_db_null


@pytest.fixture(scope="session")
async def api_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        responce = await ac.get("/")
        assert responce.status_code == 200
        yield ac


@pytest.fixture(scope="function")
async def setup_package_type():
    title = "новый уникальный тип посылок"
    data = PackageTypeBase(name=title)
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        new_data = await db.package_types.add(data)
        await db.commit()
        return new_data["id"]
