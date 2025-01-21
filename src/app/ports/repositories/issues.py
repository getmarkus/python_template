from typing import Callable, Iterable, Protocol
from src.domain.issue import Issue

class IssueRepository(Protocol):
    # or get
    async def get_by_id(self, id: int) -> Issue:
        ...

    # or get_all
    async def list(self) -> Iterable[Issue]:
        # return []
        ...

    async def list_with_predicate(self, predicate: Callable[[Issue], bool]) -> Iterable[Issue]:
        # for item in self.list():
        #    if predicate(item):
        #        yield item
        # return filter(predicate, self.list())
        ...

    async def add(self, entity: Issue) -> None:
        ...

    async def update(self, entity: Issue) -> None:
        ...

    async def remove(self, entity: Issue) -> None:
        ...