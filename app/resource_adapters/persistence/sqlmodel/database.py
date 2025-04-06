from typing import Annotated, Generator

from fastapi import Depends
from loguru import logger
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, MetaData
from sqlalchemy import text, schema

from config import Settings, get_settings

_engine: Engine | None = None
_metadata: MetaData | None = None


def get_metadata(
    settings: Annotated[Settings, Depends(get_settings)],
) -> MetaData:
    """Dependency that provides SQLModel metadata with the correct schema configuration."""
    global _metadata

    if _metadata is None:
        _metadata = MetaData(schema=settings.get_table_schema)

        # Optional: Add naming convention for constraints
        # _metadata.naming_convention = {
        #     "ix": "ix_%(column_0_label)s",
        #     "uq": "uq_%(table_name)s_%(column_0_name)s",
        #     "ck": "ck_%(table_name)s_%(constraint_name)s",
        #     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        #     "pk": "pk_%(table_name)s"
        # }

    return _metadata


MetadataDep = Annotated[MetaData, Depends(get_metadata)]


def get_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Generator[Session, Settings, None]:
    with Session(_engine) as session:
        """ session.connection(
            execution_options={
                "schema_translate_map": {None: settings.get_table_schema}
            }
        ) """
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_engine(_settings: Settings | None = None) -> Engine:
    """Get or create SQLModel engine instance."""
    global _engine

    if _engine is not None:
        return _engine

    if _settings is None:
        _settings = get_settings()

    # Configure engine based on database type
    engine_args = {"echo": True}

    # Add SQLite-specific settings for in-memory database
    if _settings.database_url.startswith("sqlite"):
        engine_args.update(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        )

    _engine = create_engine(_settings.database_url, **engine_args)

    # Enable WAL mode if configured
    if _settings.sqlite_wal_mode:
        with _engine.connect() as conn:
            # https://www.sqlite.org/pragma.html
            conn.execute(text("PRAGMA journal_mode=WAL"))
            # conn.execute(text("PRAGMA synchronous=OFF"))
            logger.info("SQLite WAL mode enabled")

    # Initialize schema if using SQLModel, with a schema if not sqlite
    if _settings.database_type == "sqlmodel":
        SQLModel.metadata.schema = _settings.get_table_schema
        with _engine.connect() as conn:
            """ conn.execution_options = {
                "schema_translate_map": {None: _settings.get_table_schema}
            } """
            if not _settings.database_url.startswith(
                "sqlite"
            ) and not conn.dialect.has_schema(conn, _settings.get_table_schema):
                logger.warning(
                    f"Schema '{_settings.get_table_schema}' not found in database. Creating..."
                )
                conn.execute(schema.CreateSchema(_settings.get_table_schema))
                conn.commit()

            if not _settings.migrate_database:
                SQLModel.metadata.create_all(conn)
                conn.commit()
                logger.info("Database tables created successfully")
            else:
                logger.info(
                    "Database tables already exist or migration is configured, skipping creation"
                )

    return _engine
