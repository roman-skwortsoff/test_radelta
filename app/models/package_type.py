# ruff: noqa: F821
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from app.database import Base


class PackageTypeORM(Base):
    """
    Таблица с типами посылок (одежда, электроника, разное)
    """

    __tablename__ = "package_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    packages: Mapped[list["PackageORM"]] = relationship(back_populates="type")
