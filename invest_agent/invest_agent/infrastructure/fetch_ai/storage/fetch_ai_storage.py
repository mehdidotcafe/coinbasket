from typing import Generic, TypeVar
from uagents.storage import KeyValueStore  # type: ignore
from jsonpickle import encode, decode  # type: ignore

from invest_agent.storage.storage import Storage, Version

T = TypeVar("T")


class FetchAiStorage(Storage[T], Generic[T]):
    def __init__(self, key_prefix: str, store: KeyValueStore):
        self.key_prefix = key_prefix
        self.store = store

    def get(self, key: str) -> tuple[T, Version] | None:
        value_and_version = self.store.get(self.__make_key(key))

        if value_and_version is not None:
            decoded = decode(value_and_version)  # type: ignore

            return decoded[0], decoded[1]  # type: ignore
        return None

    def has(self, key: str) -> bool:
        return self.store.has(self.__make_key(key))

    def set(self, key: str, value: T, version: Version) -> None:
        self.store.set(self.__make_key(key), encode([value, version]))

    def remove(self, key: str) -> None:
        self.store.remove(self.__make_key(key))

    def clear(self) -> None:
        self.store.clear()

    def __make_key(self, key: str) -> str:
        return f"{self.key_prefix}:{key}"
