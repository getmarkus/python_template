from types import TracebackType
from typing import Callable, Generic, Iterable, Protocol, TypeVar

T = TypeVar("T")


class RepositoryProtocol(Protocol, Generic[T]):
    # or get
    def get_by_id(self, id: int) -> T:
        ...

    # or get_all
    def list(self) -> Iterable[T]:
        # return []
        ...

    def list_with_predicate(self, predicate: Callable[[T], bool]) -> Iterable[T]:
        # for item in self.list():
        #    if predicate(item):
        #        yield item
        # return filter(predicate, self.list())
        ...

    def add(self, entity: T) -> None:
        ...

    def delete(self, entity: T) -> None:
        ...

    # or update
    def edit(self, entity: T) -> None:
        ...


class ConnectionProtocol(Protocol):
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


class UnitOfWorkProtocol(Protocol, Generic[T]):
    def __init__(self, connection: T) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(self) -> "UnitOfWorkProtocol[T]":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        ...
