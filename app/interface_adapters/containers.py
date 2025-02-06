from dependency_injector import containers, providers
from sqlmodel import Session

from app.resource_adapters.persistence.in_memory.issues import InMemoryIssueRepository
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository
from config import settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app"])

    # Database
    db_engine = providers.Singleton(get_engine)
    db_session = providers.Factory(Session, bind=db_engine)

    # Repositories
    issue_repository = providers.Factory(
        (
            SQLModelIssueRepository
            if settings.execution_mode == "sqlmodel"
            else InMemoryIssueRepository
        ),
        session=db_session if settings.execution_mode == "sqlmodel" else None,
    )
