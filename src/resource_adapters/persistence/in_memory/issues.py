from typing import Callable, Iterable, List

from loguru import logger

from src.app.ports.repositories.issues import IssueRepository
from src.domain.issue import Issue


class InMemoryIssueRepository(IssueRepository):
    def __init__(self) -> None:
        self.issues: List[Issue] = []
        # self.issues: dict[int, Issue] = {}
        # self.data = {}

    async def get_by_id(self, id: int) -> Issue:
        logger.info(f"getting issue by id: {id}")
        for issue in self.issues:
            if issue.issue_number == id:
                return issue
        return Issue(issue_number=0, version=0)
        # return self.issues.get(id)
        # copy.deepcopy(self.issues[id])
        # return self.data.get(key)

    async def list(self) -> List[Issue]:
        return self.issues
        # return self.issues.values()

    """
    def name_starts_with_a(user: User) -> bool:
    return user.name.startswith("A")
    # Now, using the list_with_predicate function to get users with names starting with 'A'
    users_with_a = user_repo.list_with_predicate(name_starts_with_a)
    """

    async def list_with_predicate(
        self, predicate: Callable[[Issue], bool]
    ) -> List[Issue]:
        return [issue for issue in self.issues if predicate(issue)]
        # return filter(predicate, self.issues.values())

    async def add(self, entity: Issue) -> None:
        logger.info(f"adding issue: {entity.issue_number}")
        self.issues.append(entity)
        # self.issues[entity.number] = entity
        # if key in self.data:
        #     return False
        # self.data[key] = value
        # return True

    async def update(self, entity: Issue) -> None:
        logger.info(f"updating issue: {entity}")
        for i, issue in enumerate(self.issues):
            if issue.issue_number == entity.issue_number:
                self.issues[i] = entity
                break
        # self.issues[entity.issue_number] = entity

    async def remove(self, entity: Issue) -> None:
        logger.info(f"removing issue: {entity}")
        self.issues = [i for i in self.issues if i.issue_number != entity.issue_number]
        # if entity in self.issues:
        #   self.issues.remove(entity)
        # if key in self.data:
        #     del self.data[key]
        #     return True
        # return False
