# ruff: noqa: E402
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
import uvicorn
import logging
import sys
from pathlib import Path
from fastapi_cache import FastAPICache
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.backends.redis import RedisBackend


sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)

from app.setup_indexes import ensure_mongo_indexes
from app.tasks.tasks import set_usd_course
from app.api import analytics, package_types, packages
from app.setup import redis_manager, mongo_manager
from app.middleware.session import session_key_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    await mongo_manager.connect()
    mongo_db = await mongo_manager.get_mongodb()
    app.state.mongo_db: Any = mongo_db  # type: ignore
    await ensure_mongo_indexes(mongo_db)
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    set_usd_course.delay()
    yield
    await redis_manager.close()
    await mongo_manager.close()


app = FastAPI(lifespan=lifespan)

app.middleware("http")(session_key_middleware)

# # Раскомментируйте, чтобы добавить API ключ для защиты
# if settings.MODE == "PROD":
#     app.middleware("http")(api_key_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def func():
    return "Hello World!"


app.include_router(package_types.router)
app.include_router(packages.router)
app.include_router(analytics.router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
