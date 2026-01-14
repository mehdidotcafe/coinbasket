from abc import ABC
from typing import Any, NotRequired, Type, TypeVar, TypedDict

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


class HttpRequest(ABC):
    async def get(self, params: GetParams, schema: Type[T]) -> T:
        raise NotImplementedError

    async def get_raw(self, params: GetParams) -> Any:
        raise NotImplementedError

    async def post(self, params: PostParams, schema: Type[T]) -> T:
        raise NotImplementedError
