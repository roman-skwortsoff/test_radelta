# ruff: noqa: F821
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from decimal import Decimal

from app.database import Base


class PackageORM(Base):
    """
    Таблица с посылками
    """

    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    value_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    type_id: Mapped[int] = mapped_column(ForeignKey("package_types.id"), nullable=False)
    type: Mapped["PackageTypeORM"] = relationship(back_populates="packages")

    delivery_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Europe/Moscow"))
    )

    session_id: Mapped[str] = mapped_column(String(255), index=True)
