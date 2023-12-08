from abc import abstractmethod
from typing import Protocol

from loguru import logger

from src.app_core.repository import (
    ConnectionProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)
from src.domain.issue import Issue


class AnalyzeIssueProtocol(Protocol):
    @abstractmethod
    def analyze(self) -> Issue:
        raise NotImplementedError


class AnalyzeIssue(AnalyzeIssueProtocol):
    issue_number: int = 0

    def __init__(
        self,
        issue_number: int,
        repo: RepositoryProtocol[Issue],
        unit_of_work: UnitOfWorkProtocol[ConnectionProtocol],
    ) -> None:
        self.issue_number = issue_number
        self.repo = repo
        self.unit_of_work = unit_of_work

    def analyze(self) -> Issue:
        logger.info(f"use case for analyze_issue: {self.issue_number}")
        with self.unit_of_work:
            issue: Issue = self.repo.get_by_id(self.issue_number)
            if issue.issue_number == 0:
                logger.info(f"issue not found, creating new issue: {self.issue_number}")
                issue.issue_number = self.issue_number
                issue.version = 1
                self.repo.add(issue)
        return issue
