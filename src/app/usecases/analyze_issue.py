from abc import abstractmethod
from typing import Protocol

from loguru import logger

from src.app.ports.repositories.issues import IssueRepository
from src.app.repository import (
    UnitOfWork,
)
from src.domain.issue import Issue


class AnalyzeIssueProtocol(Protocol):
    @abstractmethod
    def analyze(self) -> Issue:
        raise NotImplementedError


class AnalyzeIssue(AnalyzeIssueProtocol):
    # or could be a DTO as a inner class
    # or could be a empty/minimal Issue object
    issue_number: int = 0

    def __init__(
        self,
        issue_number: int,
        repo: IssueRepository,
        unit_of_work: UnitOfWork,
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
        # or could be a DTO as a inner class
        return issue
