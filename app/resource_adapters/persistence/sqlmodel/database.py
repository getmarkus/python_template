from typing import Annotated, Generator

from fastapi import Depends
from loguru import logger
from sqlalchemy import inspect, schema, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from config import Settings, get_settings

_engine: Engine | None = None


def get_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Generator[Session, Settings, None]:
    with Session(_engine) as session:
        session.connection(
            execution_options={"schema_translate_map": {None: settings.database_schema}}
        )
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_engine(_settings: Settings | None = None) -> Engine:
    """Get or create SQLModel engine instance."""
    global _engine

    if _engine is not None:
        return _engine

    if _settings is None:
        _settings = get_settings()

    database_url = _settings.database_url

    # Configure engine based on database type
    engine_args = {"echo": True}

    # Add SQLite-specific settings for in-memory database
    if database_url == "sqlite://":
        engine_args.update(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        )

    _engine = create_engine(database_url, **engine_args)

    # Enable WAL mode if configured
    if _settings.sqlite_wal_mode:
        with _engine.connect() as conn:
            # https://www.sqlite.org/pragma.html
            conn.execute(text("PRAGMA journal_mode=WAL"))
            # conn.execute(text("PRAGMA synchronous=OFF"))
            logger.info("SQLite WAL mode enabled")

    # Initialize database if using SQLModel
    if (
        _settings.database_type == "sqlmodel"
        and _settings.database_schema
        and not _settings.database_url.startswith("sqlite")
    ):
        SQLModel.metadata.schema = _settings.database_schema
        with _engine.connect() as conn:
            conn.execution_options = {
                "schema_translate_map": {None: _settings.database_schema}
            }
            if not conn.dialect.has_schema(conn, _settings.database_schema):
                logger.warning(
                    f"Schema '{_settings.database_schema}' not found in database. Creating..."
                )
                conn.execute(schema.CreateSchema(_settings.database_schema))
                conn.commit()

    if _settings.database_type == "sqlmodel" and not _settings.migrate_database:
        logger.info("Creating database tables...")

        # Check if tables exist before creating them
        inspector = inspect(_engine)
        existing_tables = inspector.get_table_names(
            schema=_settings.database_schema if _settings.database_schema else None
        )
        if not existing_tables:
            # if settings.database_schema:
            #     # Create schema if it doesn't exist
            #     if not inspector.has_schema(settings.database_schema):
            #         logger.info(f"Creating schema '{settings.database_schema}'")
            #         with _engine.begin() as conn:
            #             conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {settings.database_schema}'))
            SQLModel.metadata.create_all(_engine)
            logger.info("Database tables created successfully")
        else:
            logger.info("Database tables already exist, skipping creation")

    return _engine
