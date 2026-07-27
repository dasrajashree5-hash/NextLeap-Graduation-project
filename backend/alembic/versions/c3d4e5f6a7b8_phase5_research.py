"""Phase 5 research repository fields and opportunities table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("interviews") as batch_op:
            batch_op.add_column(sa.Column("discovery_barriers", sa.String(length=255), nullable=True))
            batch_op.add_column(sa.Column("coding_json", sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column("coding_version", sa.String(length=32), nullable=True))
    else:
        op.add_column("interviews", sa.Column("discovery_barriers", sa.String(length=255), nullable=True))
        op.add_column("interviews", sa.Column("coding_json", sa.JSON(), nullable=True))
        op.add_column("interviews", sa.Column("coding_version", sa.String(length=32), nullable=True))

    op.create_table(
        "opportunities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("insight_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("reach_score", sa.Float(), nullable=False),
        sa.Column("severity_score", sa.Float(), nullable=False),
        sa.Column("north_star_score", sa.Float(), nullable=False),
        sa.Column("effort_score", sa.Float(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("scoring_rationale", sa.JSON(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["insight_id"], ["insights.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("opportunities")
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("interviews") as batch_op:
            batch_op.drop_column("coding_version")
            batch_op.drop_column("coding_json")
            batch_op.drop_column("discovery_barriers")
    else:
        op.drop_column("interviews", "coding_version")
        op.drop_column("interviews", "coding_json")
        op.drop_column("interviews", "discovery_barriers")
