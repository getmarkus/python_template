from typing import Annotated
from fastapi import APIRouter, Depends
from loguru import logger
from src.app_core.config import settings
from src.app_core.repository import (
    ConnectionProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)

from src.app_core.app_core import ApplicationFacade
from src.domain.issue import Issue
from src.resource_adapters.in_memory.issue_repository import IssueRepository
from src.resource_adapters.in_memory.unit_of_work import Connection, UnitOfWork
from typing import Optional

router = APIRouter()


# https://fastapi.tiangolo.com/tutorial/dependencies/
def configure_unit_of_work() -> Optional[UnitOfWork]:
    if settings.execution_mode == "in-memory":
        return UnitOfWork(Connection())
    else:
        return None


def configure_repository() -> Optional[IssueRepository]:
    if settings.execution_mode == "in-memory":
        return IssueRepository()
    else:
        return None


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
def analyze_issue(
    issue_number: int,
    repo: Annotated[RepositoryProtocol[Issue], Depends(configure_repository)],
    uow: Annotated[
        UnitOfWorkProtocol[ConnectionProtocol], Depends(configure_unit_of_work)
    ],
) -> Issue:
    logger.info(f"post for analyze_issue: {issue_number}")
    issue: Issue = ApplicationFacade.analyze_issue(
        issue_number=issue_number, repo=repo, unit_of_work=uow
    )

    return issue
