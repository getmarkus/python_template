from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session

from config import Settings
from app.core.ports.repositories.issues import IssueRepository
from app.core.usecases.analyze_issue import AnalyzeIssue
from app.domain.issue import Issue
from app.interface_adapters.exceptions import UnsupportedOperationException
from app.resource_adapters.persistence.in_memory.issues import InMemoryIssueRepository
from app.resource_adapters.persistence.sqlmodel.database import get_db
from app.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository

router = APIRouter()


# https://fastapi.tiangolo.com/tutorial/dependencies/
def configure_repository(
    session: Annotated[Session, Depends(get_db)]
) -> IssueRepository:
    execution_mode = Settings.get_settings().execution_mode
    if execution_mode == "in-memory":
        return InMemoryIssueRepository()
    elif execution_mode == "sqlmodel":
        return SQLModelIssueRepository(session)
    else:
        raise UnsupportedOperationException(
            message="Unsupported repository configuration",
            detail=f"Execution mode '{execution_mode}' is not supported",
        )


@router.post("/issues/{issue_number}/analyze", response_model=Issue)
def analyze_issue(
    issue_number: int,
    repo: Annotated[IssueRepository, Depends(configure_repository)]
) -> Issue:
    logger.info(f"analyzing issue: {issue_number}")
    use_case = AnalyzeIssue(issue_number=issue_number, repo=repo)
    return use_case.analyze()
