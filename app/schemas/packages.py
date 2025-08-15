from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, condecimal, field_validator

from app.schemas.package_types import PackageTypeBase, PackageTypeRead


class PackageBase(BaseModel):
    name: str
    weight_kg: condecimal(gt=0, max_digits=6, decimal_places=3)
    value_usd: condecimal(gt=0, max_digits=10, decimal_places=2)

    # Округляем до 3 знаков после запятой
    @field_validator("weight_kg", mode="before")
    @classmethod
    def round_weight(cls, v):
        if v is None:
            return v
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


class PackageCreate(PackageBase):
    type_id: int


class PackageAddData(PackageCreate):
    session_id: str


class PackageRead(PackageBase):
    id: int
    type: PackageTypeRead
    delivery_cost: Optional[Decimal] | str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ниже отдельная схема для вывода списка посылок, в репозитории можно поменять на PackageRead
class PackageBrif(BaseModel):
    id: int
    name: str
    type: PackageTypeBase
    weight_kg: Decimal
    delivery_cost: Optional[Decimal] | str

    model_config = ConfigDict(from_attributes=True)
