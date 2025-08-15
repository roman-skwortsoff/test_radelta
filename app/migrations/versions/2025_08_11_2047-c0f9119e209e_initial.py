"""initial

Revision ID: c0f9119e209e
Revises:
Create Date: 2025-08-11 20:47:12.803759

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0f9119e209e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "package_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "packages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=6, scale=3), nullable=False),
        sa.Column("value_usd", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("delivery_cost", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["package_types.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_packages_session_id"), "packages", ["session_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_packages_session_id"), table_name="packages")
    op.drop_table("packages")
    op.drop_table("package_types")
