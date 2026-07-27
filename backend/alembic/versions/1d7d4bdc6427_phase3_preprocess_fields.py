"""phase3 preprocess fields

Revision ID: 1d7d4bdc6427
Revises: aede502fc485
Create Date: 2026-07-27 15:33:02.938206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1d7d4bdc6427'
down_revision: Union[str, None] = 'aede502fc485'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(col["name"] == column for col in insp.get_columns(table))


def _has_index(table: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(ix["name"] == index_name for ix in insp.get_indexes(table))


def upgrade() -> None:
    if not _has_column("reviews", "language_confidence"):
        op.add_column("reviews", sa.Column("language_confidence", sa.Float(), nullable=True))
    if not _has_column("reviews", "preprocessing_version"):
        op.add_column(
            "reviews", sa.Column("preprocessing_version", sa.String(length=32), nullable=True)
        )
    if not _has_column("reviews", "token_count"):
        op.add_column("reviews", sa.Column("token_count", sa.Integer(), nullable=True))
    if not _has_column("reviews", "needs_chunking"):
        op.add_column(
            "reviews",
            sa.Column("needs_chunking", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if not _has_index("reviews", "ix_reviews_preprocessing_version"):
        op.create_index(
            op.f("ix_reviews_preprocessing_version"),
            "reviews",
            ["preprocessing_version"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_preprocessing_version"), table_name="reviews")
    op.drop_column("reviews", "needs_chunking")
    op.drop_column("reviews", "token_count")
    op.drop_column("reviews", "preprocessing_version")
    op.drop_column("reviews", "language_confidence")
