from app.repositories.package import PackageRepository
from app.repositories.package_types import PackageTypeRepository


class DB_Manager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.packages = PackageRepository(self.session)
        self.package_types = PackageTypeRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
