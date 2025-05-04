from typing import Generic, TypeVar
from uagents.storage import KeyValueStore
from jsonpickle import encode, decode

from coinbasket.storage.storage import Storage

T = TypeVar("T")


class FetchAiStorage(Storage[T], Generic[T]):
    def __init__(self, key_prefix: str, store: KeyValueStore):
        self.key_prefix = key_prefix
        self.store = store

    def get(self, key: str) -> T | None:
        value = self.store.get(self.__make_key(key))

        if value is not None:
            return decode(value)  # type: ignore[no-untyped-call]
        return value

    def has(self, key: str) -> bool:
        return self.store.has(self.__make_key(key))

    def set(self, key: str, value: T) -> None:
        self.store.set(self.__make_key(key), encode(value))

    def remove(self, key: str) -> None:
        self.store.remove(self.__make_key(key))

    def clear(self) -> None:
        self.store.clear()

    def __make_key(self, key: str) -> str:
        return f"{self.key_prefix}:{key}"
