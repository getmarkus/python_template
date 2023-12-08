from loguru import logger

from src.app_core.usecases.analyze_issue import AnalyzeIssue
from src.app_core.repository import (
    ConnectionProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)
from src.domain.issue import Issue


class ApplicationFacade:
    @staticmethod
    def analyze_issue(
        issue_number: int,
        repo: RepositoryProtocol[Issue],
        unit_of_work: UnitOfWorkProtocol[ConnectionProtocol],
    ) -> Issue:
        # this is where you would get the user
        logger.info(f"appfacade for analyze_issue: {issue_number}")
        issue: Issue = AnalyzeIssue(
            issue_number=issue_number, repo=repo, unit_of_work=unit_of_work
        ).analyze()
        return issue
