"""phase4 analysis fields

Revision ID: b2c3d4e5f6a7
Revises: 1d7d4bdc6427
Create Date: 2026-07-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "1d7d4bdc6427"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(col["name"] == column for col in insp.get_columns(table))


def _has_insights_theme_fk() -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(
        "theme_id" in fk.get("constrained_columns", [])
        for fk in insp.get_foreign_keys("insights")
    )


def _add_insights_theme_id() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("insights") as batch_op:
            batch_op.add_column(sa.Column("theme_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_insights_theme_id",
                "themes",
                ["theme_id"],
                ["id"],
            )
    else:
        op.add_column("insights", sa.Column("theme_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_insights_theme_id",
            "insights",
            "themes",
            ["theme_id"],
            ["id"],
        )


def upgrade() -> None:
    if not _has_column("reviews", "analysis_version"):
        op.add_column(
            "reviews",
            sa.Column("analysis_version", sa.String(length=32), nullable=True),
        )
        op.create_index("ix_reviews_analysis_version", "reviews", ["analysis_version"])
    if not _has_column("reviews", "analysis_failed"):
        op.add_column(
            "reviews",
            sa.Column(
                "analysis_failed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )

    if not _has_column("analyses", "sentiment_intensity"):
        op.add_column("analyses", sa.Column("sentiment_intensity", sa.Float(), nullable=True))
    if not _has_column("analyses", "complaint_category"):
        op.add_column(
            "analyses", sa.Column("complaint_category", sa.String(length=128), nullable=True)
        )
    if not _has_column("analyses", "shopping_behaviour"):
        op.add_column("analyses", sa.Column("shopping_behaviour", sa.Text(), nullable=True))
    if not _has_column("analyses", "discovery_json"):
        op.add_column("analyses", sa.Column("discovery_json", sa.JSON(), nullable=True))
    if not _has_column("analyses", "status"):
        op.add_column(
            "analyses",
            sa.Column("status", sa.String(length=32), nullable=False, server_default="success"),
        )

    if not _has_column("insights", "confidence_breakdown"):
        op.add_column("insights", sa.Column("confidence_breakdown", sa.JSON(), nullable=True))
    if not _has_column("insights", "rank_score"):
        op.add_column("insights", sa.Column("rank_score", sa.Float(), nullable=True))
    if not _has_column("insights", "theme_id"):
        _add_insights_theme_id()
    elif not _has_insights_theme_fk():
        bind = op.get_bind()
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("insights") as batch_op:
                batch_op.create_foreign_key(
                    "fk_insights_theme_id",
                    "themes",
                    ["theme_id"],
                    ["id"],
                )
        else:
            op.create_foreign_key(
                "fk_insights_theme_id",
                "insights",
                "themes",
                ["theme_id"],
                ["id"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("insights") as batch_op:
            batch_op.drop_constraint("fk_insights_theme_id", type_="foreignkey")
            batch_op.drop_column("theme_id")
    else:
        op.drop_constraint("fk_insights_theme_id", "insights", type_="foreignkey")
        op.drop_column("insights", "theme_id")
    op.drop_column("insights", "rank_score")
    op.drop_column("insights", "confidence_breakdown")
    op.drop_column("analyses", "status")
    op.drop_column("analyses", "discovery_json")
    op.drop_column("analyses", "shopping_behaviour")
    op.drop_column("analyses", "complaint_category")
    op.drop_column("analyses", "sentiment_intensity")
    op.drop_column("reviews", "analysis_failed")
    op.drop_index("ix_reviews_analysis_version", table_name="reviews")
    op.drop_column("reviews", "analysis_version")
