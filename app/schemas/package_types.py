from pydantic import BaseModel, ConfigDict


class PackageTypeBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class PackageTypeRead(PackageTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
