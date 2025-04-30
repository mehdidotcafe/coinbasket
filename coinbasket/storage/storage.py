from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class Storage(ABC, Generic[T]):
    @abstractmethod
    def get(self, key: str) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def has(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
