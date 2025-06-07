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

    # Get the base URL template and credentials
    url_template = _settings.database_url_template
    username = _settings.app_db_user
    password = _settings.app_db_password.get_secret_value() if _settings.app_db_password else None
    
    # Determine if we're using PostgreSQL or SQLite
    is_postgres = url_template.startswith("postgresql") or url_template.startswith("postgres")
    
    if is_postgres:
        # For PostgreSQL, create the URL with explicit credentials
        from urllib.parse import quote_plus
        
        # Extract the host, port, and database name from the template
        if "@" in url_template:
            protocol_part, rest = url_template.split("://", 1)
            _, server_part = rest.split("@", 1)
        else:
            protocol_part, server_part = url_template.split("://", 1)
        
        # We'll use psycopg for sync connections regardless of the original driver
        
        # Use psycopg for sync connections
        sync_driver = "postgresql+psycopg"
        
        # Create the URL with explicit credentials
        url = f"{sync_driver}://{username}:{quote_plus(password)}@{server_part}"
        logger.debug(f"Database connection prepared with driver: {sync_driver}")
    else:
        # For SQLite or other databases, use the template as is
        url = url_template
        logger.debug("Using database URL template as is: {}".format(url_template))
    
    # Log the connection attempt
    logger.debug("Database connection URL created (password masked in logs)")
    try:
        from sqlalchemy.engine import make_url
        # Just for validation purposes
        make_url(url)
    except ImportError:
        logger.warning("Could not import sqlalchemy.engine.make_url")

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
                conn,
                _settings.get_table_schema,  # type: ignore[arg-type]
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
        engine_args.update(
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        )

    _async_engine = create_async_engine(url, **engine_args)
    _async_sessionmaker = sessionmaker(
        _async_engine, class_=AsyncSession, expire_on_commit=False
    )
    return _async_engine


async def get_async_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    engine = get_async_engine(settings)
    assert _async_sessionmaker is not None
    async with _async_sessionmaker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
