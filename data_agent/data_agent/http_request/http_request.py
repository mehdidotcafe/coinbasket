from abc import ABC
from typing import Any, Generic, NotRequired, TypeVar, TypedDict


T = TypeVar("T")


class GetParams(TypedDict):
    url: str
    params: NotRequired[dict[str, Any]]
    headers: NotRequired[dict[str, Any]]


class HttpRequest(ABC, Generic[T]):
    def get(self, params: GetParams) -> T:
        raise NotImplementedError
