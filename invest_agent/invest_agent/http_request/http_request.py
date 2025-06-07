from abc import ABC
from typing import Any, Generic, NotRequired, TypeVar, TypedDict

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class GetParams(TypedDict):
    url: str
    params: NotRequired[dict[str, Any]]
    headers: NotRequired[dict[str, Any]]


class PostParams(TypedDict):
    url: str
    body: NotRequired[dict[str, Any]]
    headers: NotRequired[dict[str, Any]]


class HttpRequest(ABC, Generic[T]):
    async def get(self, params: GetParams, schema: T) -> T:
        raise NotImplementedError

    async def post(self, params: PostParams, schema: T) -> T:
        raise NotImplementedError
