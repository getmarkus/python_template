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
async def configure_unit_of_work() -> Optional[UnitOfWork]:
    if Settings.get_settings().execution_mode == "in-memory":
        return UnitOfWork()
    else:
        return None


async def configure_repository() -> Optional[InMemoryIssueRepository]:
    if Settings.get_settings().execution_mode == "in-memory":
        return InMemoryIssueRepository()
    else:
        return None


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
async def analyze_issue(
    issue_number: int,
    unit_of_work: Annotated[UnitOfWork, Depends(configure_unit_of_work)],
    repo: Annotated[InMemoryIssueRepository, Depends(configure_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AnalyzeIssue(issue_number=issue_number, repo=repo, unit_of_work=unit_of_work)
    return await use_case.analyze()
