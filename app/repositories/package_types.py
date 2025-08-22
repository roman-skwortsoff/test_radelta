from app.models.package_type import PackageTypeORM
from app.schemas.package_types import PackageTypeRead
from app.repositories.base import BaseRepository


class PackageTypeRepository(BaseRepository):
    model = PackageTypeORM
    schema = PackageTypeRead
