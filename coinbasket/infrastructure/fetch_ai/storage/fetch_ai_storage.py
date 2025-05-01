from typing import Generic, TypeVar
from uagents.storage import KeyValueStore
from jsonpickle import encode, decode

from coinbasket.storage.storage import Storage

T = TypeVar("T")


class FetchAiStorage(Storage[T], Generic[T]):
    def __init__(self, store: KeyValueStore):
        self.store = store

    def get(self, key: str) -> T | None:
        value = self.store.get(key)

        if value is not None:
            return decode(value)  # type: ignore[no-untyped-call]
        return value

    def has(self, key: str) -> bool:
        return self.store.has(key)

    def set(self, key: str, value: T) -> None:
        self.store.set(key, encode(value))

    def remove(self, key: str) -> None:
        self.store.remove(key)

    def clear(self) -> None:
        self.store.clear()
