"""Settings / DATABASE_URL normalization."""

from app.config import _normalize_database_url


def test_normalize_postgres_scheme():
    assert (
        _normalize_database_url("postgres://u:p@host:5432/railway")
        == "postgresql+psycopg://u:p@host:5432/railway"
    )


def test_normalize_postgresql_scheme():
    assert (
        _normalize_database_url("postgresql://u:p@host/db")
        == "postgresql+psycopg://u:p@host/db"
    )


def test_sqlite_unchanged():
    assert _normalize_database_url("sqlite:///./data/discovery.db").startswith("sqlite:")
