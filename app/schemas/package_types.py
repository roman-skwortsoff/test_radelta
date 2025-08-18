from pydantic import BaseModel, ConfigDict, Field


class PackageTypeBase(BaseModel):
    name: str = Field(..., max_length=40)

    model_config = ConfigDict(from_attributes=True)


class PackageTypeRead(PackageTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
