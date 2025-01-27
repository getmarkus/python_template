from loguru import logger
from sqlmodel import SQLModel, create_engine

from config import Settings
from src.domain.issue import Issue  # noqa: F401

_engine = None


def get_engine(database_url: str | None = None):
    """Get or create SQLModel engine instance."""
    global _engine

    if _engine is not None:
        return _engine

    if database_url is None:
        database_url = Settings.get_settings().database_url
        if not database_url:
            database_url = "sqlite:///./issues.db"
            logger.warning(f"No database URL configured, using default: {database_url}")

    _engine = create_engine(database_url,connect_args={"check_same_thread": False}, echo=True)
    return _engine


def init_db() -> None:
    """Initialize the database by creating all tables."""
    engine = get_engine()
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")
