from typing import Protocol

from loguru import logger

from app.features.issues.repository import IssueRepository
from app.domain.issue import Issue
from app.core.exceptions import NotFoundException


class AnalyzeIssue(Protocol):
    # or could be a DTO as a inner class
    # or could be a empty/minimal Issue object
    issue_number: int = 0

    def __init__(
        self,
        issue_number: int,
        repo: IssueRepository,
    ) -> None:
        self.issue_number = issue_number
        self.repo = repo

    def analyze(self) -> Issue:
        logger.info(f"analyzing issue: {self.issue_number}")
        issue = self.repo.get_by_id(self.issue_number)
        logger.info(f"issue: {issue}")
        if issue.issue_number == 0:
            logger.info(f"not found issue: {self.issue_number}")
            raise NotFoundException(
                message="Issue not found",
                detail=f"Issue with number {self.issue_number} does not exist",
            )
        return issue
