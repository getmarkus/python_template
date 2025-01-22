from typing import Annotated
from fastapi import APIRouter, Depends
from loguru import logger

from src.app.usecases.analyze_issue import AnalyzeIssue
from config import Settings
from src.domain.issue import Issue
from src.interface_adapters.exceptions import UnsupportedOperationException
from src.resource_adapters.persistence.in_memory.issues import InMemoryIssueRepository
from src.resource_adapters.persistence.in_memory.unit_of_work import UnitOfWork

router = APIRouter()


# https://fastapi.tiangolo.com/tutorial/dependencies/
async def configure_unit_of_work() -> UnitOfWork:
    if Settings.get_settings().execution_mode == "in-memory":
        return UnitOfWork()
    else:
        raise UnsupportedOperationException(
            message="Unsupported unit of work configuration",
            detail="Only in-memory unit of work is currently supported"
        )


async def configure_repository() -> InMemoryIssueRepository:
    if Settings.get_settings().execution_mode == "in-memory":
        return InMemoryIssueRepository()
    else:
        raise UnsupportedOperationException(
            message="Unsupported repository configuration",
            detail="Only in-memory repository is currently supported"
        )


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
async def analyze_issue(
    issue_number: int,
    unit_of_work: Annotated[UnitOfWork, Depends(configure_unit_of_work)],
    repo: Annotated[InMemoryIssueRepository, Depends(configure_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AnalyzeIssue(issue_number=issue_number, repo=repo, unit_of_work=unit_of_work)
    return await use_case.analyze()
