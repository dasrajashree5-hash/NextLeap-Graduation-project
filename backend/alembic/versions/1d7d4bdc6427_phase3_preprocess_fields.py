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
    rows = bind.execute(sa.text(f"PRAGMA table_info({table})")).fetchall()
    return any(row[1] == column for row in rows)


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

    bind = op.get_bind()
    indexes = bind.execute(sa.text("PRAGMA index_list(reviews)")).fetchall()
    index_names = {row[1] for row in indexes}
    if "ix_reviews_preprocessing_version" not in index_names:
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
