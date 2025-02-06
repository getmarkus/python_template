from typing import Generator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from config import settings

_engine: Engine | None = None


def get_db() -> Generator[Session, None, None]:
    with Session(_engine) as session:
        yield session


def get_engine(database_url: str | None = None) -> Engine:
    """Get or create SQLModel engine instance."""
    global _engine

    if _engine is not None:
        return _engine

    if database_url is None:
        database_url = settings.database_url

    # Configure engine based on database type
    engine_args = {"echo": True}

    # Add SQLite-specific settings for in-memory database
    if database_url == "sqlite://":
        engine_args.update(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        )

    _engine = create_engine(database_url, **engine_args)

    # Enable WAL mode if configured
    if settings.sqlite_wal_mode and database_url.startswith("sqlite"):
        with _engine.connect() as conn:
            # https://www.sqlite.org/pragma.html
            conn.execute(text("PRAGMA journal_mode=WAL"))
            # conn.execute(text("PRAGMA synchronous=OFF"))
            logger.info("SQLite WAL mode enabled")

    # Initialize database if using SQLModel
    if settings.execution_mode == "sqlmodel" and not settings.migrate_database:
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(_engine)
        logger.info("Database tables created successfully")

    return _engine
