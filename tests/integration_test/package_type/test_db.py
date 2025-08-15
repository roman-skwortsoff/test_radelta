from app.schemas.package_types import PackageTypeBase
from app.utils.db_manager import DB_Manager
from app.database import async_session_maker_null


async def test_add_package_types():
    title = "тестовый тип посылок"
    data = PackageTypeBase(name=title)
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        new_data = await db.package_types.add(data)
        await db.commit()
        assert isinstance(new_data["id"], int)
        assert new_data["id"] > 0

        saved_data = await db.package_types.get_one(id=new_data["id"])
        assert saved_data is not None
        assert saved_data.name == title
