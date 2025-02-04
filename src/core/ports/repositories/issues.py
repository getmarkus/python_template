from typing import Callable, Iterable, Protocol
from src.domain.issue import Issue

class IssueRepository(Protocol):
    # or get
    def get_by_id(self, id: int) -> Issue:
        ...

    # or get_all
    def list(self) -> Iterable[Issue]:
        # return []
        ...

    def list_with_predicate(self, predicate: Callable[[Issue], bool]) -> Iterable[Issue]:
        # for item in self.list():
        #    if predicate(item):
        #        yield item
        # return filter(predicate, self.list())
        ...

    def add(self, entity: Issue) -> None:
        ...

    def update(self, entity: Issue) -> None:
        ...

    def remove(self, entity: Issue) -> None:
        ...