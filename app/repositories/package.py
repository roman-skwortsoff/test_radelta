from decimal import Decimal

from app.exceptions import ObjectNotFoundException
from app.models.package import PackageORM
from app.models.package_type import PackageTypeORM
from app.schemas.packages import PackageBrif, PackageRead
from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseReposirory


class PackageRepository(BaseReposirory):
    model = PackageORM
    schema = PackageRead

    async def get_filtered_by_type(
        self,
        session_id: str,
        limit: int,
        offset: int,
        type_filter: str | None = None,
        has_delivery_cost: bool | None = None,
    ):
        query = (
            select(self.model)
            .options(joinedload(self.model.type))
            .filter(self.model.session_id == session_id)
        )

        # Фильтр по типу (id или name)
        if type_filter:
            if type_filter.isdigit():
                query = query.filter(self.model.type_id == int(type_filter))
            else:
                query = query.join(self.model.type).filter(
                    func.lower(PackageTypeORM.name).like(f"%{type_filter.lower()}%")
                )

        # Фильтр по delivery_cost
        if has_delivery_cost is True:
            query = query.filter(self.model.delivery_cost.isnot(None))
        elif has_delivery_cost is False:
            query = query.filter(self.model.delivery_cost.is_(None))

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)

        packages = result.scalars().all()

        for p in packages:
            if p.delivery_cost is None:
                p.delivery_cost = "Не рассчитано"

        return [PackageBrif.model_validate(package) for package in packages]

        # return [
        #     PackageBrif.model_validate(model) for model in result.scalars().all()
        # ]  # если нужны полностью все поля, то удалите эту строку
        # return [self.schema.model_validate(model) for model in result.scalars().all()] # и раскомментируете эту

    async def get_one(self, **filter_by):
        query = (
            select(self.model)
            .options(joinedload(self.model.type))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException

        if model.delivery_cost is None:
            model.delivery_cost = "Не рассчитано"

        return self.schema.model_validate(model)

    async def update_costs(self, usd_rub_rate: Decimal):
        cost_expr = func.round(
            (
                self.model.weight_kg * Decimal("0.5")
                + self.model.value_usd * Decimal("0.01")
            )
            * usd_rub_rate,
            2,
        )

        query = (
            update(self.model)
            .filter(self.model.delivery_cost.is_(None))
            .values(delivery_cost=cost_expr)
        )

        result = await self.session.execute(query)

        return result.rowcount
