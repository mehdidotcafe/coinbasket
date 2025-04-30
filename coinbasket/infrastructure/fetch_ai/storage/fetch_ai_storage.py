from typing import Generic, TypeVar
from uagents.storage import KeyValueStore

from coinbasket.storage.storage import Storage

T = TypeVar("T")


class FetchAiStorage(Storage[T], Generic[T]):
    def __init__(self, store: KeyValueStore):
        self.store = store

    def get(self, key: str) -> T | None:
        return self.store.get(key)

    def has(self, key: str) -> bool:
        return self.store.has(key)

    def set(self, key: str, value: T) -> None:
        self.store.set(key, value)

    def remove(self, key: str) -> None:
        self.store.remove(key)

    def clear(self) -> None:
        self.store.clear()
