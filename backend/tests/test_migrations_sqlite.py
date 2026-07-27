"""Alembic migrations apply cleanly on SQLite (Railway default without Postgres)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text


BACKEND_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def fresh_sqlite_url(tmp_path: Path) -> str:
    db_file = tmp_path / "migrate_test.db"
    return f"sqlite:///{db_file}"


def test_alembic_upgrade_head_sqlite(fresh_sqlite_url: str) -> None:
    env = {"DATABASE_URL": fresh_sqlite_url}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    engine = create_engine(fresh_sqlite_url)
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        assert version == "c3d4e5f6a7b8"

        insp = inspect(conn)
        assert "insights" in insp.get_table_names()
        insight_cols = {c["name"] for c in insp.get_columns("insights")}
        assert {"theme_id", "rank_score", "confidence_breakdown"}.issubset(insight_cols)

        fks = insp.get_foreign_keys("insights")
        assert any("theme_id" in fk.get("constrained_columns", []) for fk in fks)

        assert "opportunities" in insp.get_table_names()
