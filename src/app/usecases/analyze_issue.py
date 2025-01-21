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
    async def analyze(self) -> Issue:
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

    async def analyze(self) -> Issue:
        logger.info(f"analyzing issue: {self.issue_number}")
        issue = await self.repo.get_by_id(self.issue_number)
        return issue
