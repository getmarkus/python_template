from typing import Generator

from loguru import logger
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from config import Settings

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
        database_url = Settings.get_settings().database_url

    _engine = create_engine(
        database_url, echo=True
    )
    # Initialize database if using SQLModel
    if Settings.get_settings().execution_mode == "sqlmodel" and not Settings.get_settings().migrate_database:
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(_engine)
        logger.info("Database tables created successfully")
        
    return _engine

