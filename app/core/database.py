from typing import Annotated, Generator, AsyncGenerator

from fastapi import Depends
from loguru import logger
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, MetaData
from sqlalchemy import text, schema

from config import Settings, get_settings

_engine: Engine | None = None
_async_engine: AsyncEngine | None = None
_metadata: MetaData | None = None
_async_sessionmaker: sessionmaker[AsyncSession] | None = None


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

    url = _settings.database_url
    try:
        from sqlalchemy.engine import make_url

        # For migrations, strip any async driver suffix and use the sync DBAPI:
        # - PostgreSQL: always use psycopg (psycopg3) as the sync driver
        # - SQLite: use the built-in sqlite driver
        url_obj = make_url(url)
        scheme, *_ = url_obj.drivername.split("+", 1)
        if scheme in ("postgresql", "postgres"):
            # normalize to PostgreSQL with psycopg3 for sync migrations
            sync_driver = "postgresql+psycopg"
        else:
            sync_driver = scheme
        url_obj = url_obj.set(drivername=sync_driver)
        url = str(url_obj)
    except ImportError:
        pass

    engine_args: dict = {"echo": True}
    if url.startswith("sqlite"):
        engine_args.update(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        )

    _engine = create_engine(url, **engine_args)

    if _settings.sqlite_wal_mode and url.startswith("sqlite"):
        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            logger.info("SQLite WAL mode enabled")

    if _settings.database_type == "sqlmodel":
        SQLModel.metadata.schema = _settings.get_table_schema
        with _engine.connect() as conn:
            if not url.startswith("sqlite") and not conn.dialect.has_schema(
                conn, _settings.get_table_schema  # type: ignore[arg-type]
            ):
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


def get_async_engine(_settings: Settings | None = None) -> AsyncEngine:
    """Get or create async SQLModel engine instance."""
    global _async_engine, _async_sessionmaker

    if _async_engine is not None:
        return _async_engine

    if _settings is None:
        _settings = get_settings()

    url = _settings.database_url
    # SQLite: use the aiosqlite driver for async support
    if url.startswith("sqlite") and "+aiosqlite" not in url:
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    else:
        # PostgreSQL: ensure an asyncpg driver if scheme is postgres/postgresql without a +driver suffix
        try:
            scheme, rest = url.split("://", 1)
        except ValueError:
            scheme = url
            rest = ""
        if scheme in ("postgres", "postgresql") and "+" not in scheme:
            url = f"postgresql+asyncpg://{rest}"

    engine_args: dict = {"echo": True}
    if url.startswith("sqlite"):
        engine_args.update({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool})

    _async_engine = create_async_engine(url, **engine_args)
    _async_sessionmaker = sessionmaker(_async_engine, class_=AsyncSession, expire_on_commit=False)
    return _async_engine


async def get_async_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    engine = get_async_engine(settings)
    assert _async_sessionmaker is not None
    async with _async_sessionmaker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
