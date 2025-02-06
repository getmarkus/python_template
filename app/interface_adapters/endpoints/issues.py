from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends
from loguru import logger

from app.core.ports.repositories.issues import IssueRepository
from app.core.usecases.analyze_issue import AnalyzeIssue
from app.domain.issue import Issue
from app.interface_adapters.containers import Container

router = APIRouter()


def get_repository() -> IssueRepository:
    return Container.issue_repository()


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
@inject
def analyze_issue(
    issue_number: int,
    repo: Annotated[IssueRepository, Depends(get_repository)],
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AnalyzeIssue(issue_number=issue_number, repo=repo)
    return use_case.analyze()
