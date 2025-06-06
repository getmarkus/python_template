from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.features.issues.repository import IssueRepository
from app.features.issues.analyze_issue import AnalyzeIssue
from app.domain.issue import Issue
from app.core.database import SessionDep
from app.features.issues.repository import SQLModelIssueRepository

router = APIRouter()


def get_repository(session: SessionDep) -> IssueRepository:
    with SQLModelIssueRepository(session) as repo:
        yield repo


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
def analyze_issue(
    issue_number: int,
    repo: Annotated[IssueRepository, Depends(get_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AnalyzeIssue(issue_number=issue_number, repo=repo)
    return use_case.analyze()
