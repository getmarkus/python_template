from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from config import Settings
from src.app.ports.repositories.issues import IssueRepository
from src.app.repository import UnitOfWork as BaseUnitOfWork
from src.app.usecases.analyze_issue import AnalyzeIssue
from src.domain.issue import Issue
from src.interface_adapters.exceptions import UnsupportedOperationException
from src.resource_adapters.persistence.in_memory.issues import InMemoryIssueRepository
from src.resource_adapters.persistence.in_memory.unit_of_work import (
    UnitOfWork as InMemoryUnitOfWork,
)
from src.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository
from src.resource_adapters.persistence.sqlmodel.unit_of_work import SQLModelUnitOfWork

router = APIRouter()


# https://fastapi.tiangolo.com/tutorial/dependencies/
async def configure_unit_of_work() -> BaseUnitOfWork:
    execution_mode = Settings.get_settings().execution_mode
    if execution_mode == "in-memory":
        return InMemoryUnitOfWork()
    elif execution_mode == "sqlmodel":
        return SQLModelUnitOfWork(database_url=Settings.get_settings().database_url)
    else:
        raise UnsupportedOperationException(
            message="Unsupported unit of work configuration",
            detail=f"Execution mode '{execution_mode}' is not supported",
        )


async def configure_repository() -> IssueRepository:
    execution_mode = Settings.get_settings().execution_mode
    if execution_mode == "in-memory":
        return InMemoryIssueRepository()
    elif execution_mode == "sqlmodel":
        # For SQLModel, the repository is managed by the UnitOfWork
        # This is just a placeholder that will be replaced
        return SQLModelIssueRepository(None)  # type: ignore
    else:
        raise UnsupportedOperationException(
            message="Unsupported repository configuration",
            detail=f"Execution mode '{execution_mode}' is not supported",
        )


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
async def analyze_issue(
    issue_number: int,
    unit_of_work: Annotated[BaseUnitOfWork, Depends(configure_unit_of_work)],
    repo: Annotated[IssueRepository, Depends(configure_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")

    # For SQLModel, we need to use the repository from the unit of work
    if isinstance(unit_of_work, SQLModelUnitOfWork):
        repo = unit_of_work.issues

    use_case = AnalyzeIssue(
        issue_number=issue_number, repo=repo, unit_of_work=unit_of_work
    )
    return await use_case.analyze()
