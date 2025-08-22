from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.package_types import PackageTypeBase, PackageTypeRead


DecimalField = Annotated[
    Decimal,
    Field(
        ...,
        gt=0,
        json_schema_extra={
            "type": "string",
            "format": "decimal",
            "pattern": "^\\d+(\\.\\d{1,3})?$",
        },
    ),
]


class PackageBase(BaseModel):
    name: str = Field(..., max_length=40)

    weight_kg: Annotated[
        Decimal,
        Field(
            ...,
            gt=0,
            max_digits=6,
            decimal_places=3,
            json_schema_extra={"example": "1.555"},
        ),
    ]

    value_usd: Annotated[
        Decimal,
        Field(
            ...,
            gt=0,
            max_digits=10,
            decimal_places=2,
            json_schema_extra={"example": "15.55"},
        ),
    ]

    @field_validator("weight_kg", mode="before")
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
    delivery_cost: Union[Decimal, str] = Field(
        ...,
        examples=["150.50", "Не рассчитано"],
        json_schema_extra={
            "oneOf": [
                {"type": "string", "format": "decimal", "example": "150.50"},
                {"type": "string", "example": "Не рассчитано"},
            ]
        },
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PackageBrief(BaseModel):
    id: int
    name: str
    type: PackageTypeBase
    weight_kg: Decimal = Field(..., json_schema_extra={"example": "1.500"})
    delivery_cost: Union[Decimal, str] = Field(
        ...,
        examples=["150.50", "Не рассчитано"],
        json_schema_extra={
            "oneOf": [
                {"type": "string", "format": "decimal", "example": "150.50"},
                {"type": "string", "example": "Не рассчитано"},
            ]
        },
    )

    model_config = ConfigDict(from_attributes=True)
