from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool

from app.config import settings


engine = create_async_engine(settings.DB_URL, echo=True)
engine_null = create_async_engine(settings.DB_URL, echo=True, poolclass=NullPool)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null = async_sessionmaker(bind=engine_null, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
