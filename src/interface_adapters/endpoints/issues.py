from typing import Annotated
from fastapi import APIRouter, Depends
from loguru import logger

from src.app.usecases.analyze_issue import AnalyzeIssue
from config import Settings

from src.domain.issue import Issue
from src.resource_adapters.persistence.in_memory.issues import InMemoryIssueRepository
from src.resource_adapters.persistence.in_memory.unit_of_work import UnitOfWork
from typing import Optional

router = APIRouter()


# https://fastapi.tiangolo.com/tutorial/dependencies/
def configure_unit_of_work() -> Optional[UnitOfWork]:
    if Settings.get_settings().execution_mode == "in-memory":
        return UnitOfWork()
    else:
        return None


def configure_repository() -> Optional[InMemoryIssueRepository]:
    if Settings.get_settings().execution_mode == "in-memory":
        return InMemoryIssueRepository()
    else:
        return None


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
def analyze_issue(
    issue_number: int,
    repo: Annotated[InMemoryIssueRepository, Depends(configure_repository)],
    uow: Annotated[UnitOfWork, Depends(configure_unit_of_work)],
) -> Issue:
    logger.info(f"post for analyze_issue: {issue_number}")
    issue: Issue = AnalyzeIssue(
        issue_number=issue_number, repo=repo, unit_of_work=uow
    ).analyze()

    return issue
