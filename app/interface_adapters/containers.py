from dependency_injector import containers, providers
from sqlmodel import Session

from app.resource_adapters.persistence.collections.issues import (
    CollectionIssueRepository,
)
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository
from config import settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app"])

    # Database
    db_engine = providers.Singleton(get_engine)
    db_session = providers.Factory(Session, bind=db_engine)

    # Repositories
    sqlmodel_repository = providers.Factory(SQLModelIssueRepository, session=db_session)

    collection_repository = providers.Factory(CollectionIssueRepository)

    def get_model_config():
        return settings.model_config

    issue_repository = providers.Selector(
        get_model_config,
        sqlmodel=sqlmodel_repository,
        **{"collection": collection_repository},
    )
