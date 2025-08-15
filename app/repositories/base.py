from pydantic import BaseModel
import logging
from sqlalchemy import select, insert, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.exceptions import (
    ObjectNotFoundException,
    DataBaseIntegrityException,
    ObjectAlreadyExistException,
)


class BaseReposirory:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.schema.model_validate(model)

    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump())
        try:
            result = await self.session.execute(add_stmt)

        except IntegrityError as ex:
            if hasattr(ex.orig, "args") and len(ex.orig.args) > 0:
                error_code = ex.orig.args[0]
                if error_code == 1062:
                    logging.exception(
                        f"Не удалось добавить данные — дубликат, входные данные={data}"
                    )
                    raise ObjectAlreadyExistException from ex
            logging.error(
                f"Незнакомая ошибка добавления в БД. Входные данные:{data}. Ошибка: {ex}"
            )
            raise DataBaseIntegrityException from ex

        inserted_id = result.lastrowid
        return {"id": inserted_id}

    async def delete(self, **filter_by) -> None:
        await self.get_one(**filter_by)
        stmt = delete(self.model).filter_by(**filter_by)
        try:
            await self.session.execute(stmt)
        except IntegrityError:
            raise DataBaseIntegrityException
        else:
            return {"status": "ok"}
