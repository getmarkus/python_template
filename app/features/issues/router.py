from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from app.core.database import AsyncSessionDep
from app.features.issues.repository import AsyncSQLModelIssueRepository
from app.features.issues.analyze_issue_async import AsyncAnalyzeIssue
from app.domain.issue import Issue

router = APIRouter()


async def get_repository(session: AsyncSessionDep) -> AsyncSQLModelIssueRepository:
    async with AsyncSQLModelIssueRepository(session) as repo:
        yield repo


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
async def analyze_issue(
    issue_number: int,
    repo: Annotated[AsyncSQLModelIssueRepository, Depends(get_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AsyncAnalyzeIssue(issue_number=issue_number, repo=repo)
    return await use_case.analyze()
