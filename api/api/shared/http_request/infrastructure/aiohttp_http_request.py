from typing import Any, Type, TypeVar
from pydantic import BaseModel
import aiohttp

from api.shared.http_request.exception.failed_request import (
    FailedRequest,
)
from api.shared.http_request.http_request import (
    ConfigurationDict,
    GetParams,
    HttpRequest,
    PostParams,
)


T = TypeVar("T", bound=BaseModel)


class AiohttpHttpRequest(HttpRequest):
    TIMEOUT = 20  # seconds

    def __init__(self, configuration: ConfigurationDict):
        self._configuration = configuration

    def _get_headers(self, headers: dict[str, Any] = None) -> dict[str, Any]:
        base_headers = {"Origin": self._configuration["app_domain"]}

        return {**base_headers, **(headers or {})}

    async def get(self, params: GetParams, schema: Type[T]) -> T:
        """
        Fetches data from a given URL using the aiohttp library.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                params.get("url"),
                params=params.get("params"),
                headers=self._get_headers(params.get("headers")),
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as response:
                if response.status >= 200 and response.status < 400:
                    json_response = await response.json()

                    return schema.model_validate(json_response)

                print(f"Failed request: {response.status} {await response.text()}")

                raise FailedRequest(
                    status_code=response.status,
                    response=await response.text(),
                )

    async def get_raw(self, params: GetParams) -> Any:
        """
        Fetches raw data from a given URL using the aiohttp library.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                params.get("url"),
                params=params.get("params"),
                headers=self._get_headers(params.get("headers")),
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as response:
                if response.status >= 200 and response.status < 400:
                    return await response.json()

                print(f"Failed request: {response.status} {await response.text()}")

                raise FailedRequest(
                    status_code=response.status,
                    response=await response.text(),
                )

    async def post(self, params: PostParams, schema: Type[T]) -> T:
        """
        Sends a POST request to a given URL using the aiohttp library.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                params.get("url"),
                json=params.get("body"),
                headers=self._get_headers(params.get("headers")),
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as response:
                if response.status >= 200 and response.status < 400:
                    return schema.model_validate(await response.json())
                raise FailedRequest(
                    status_code=response.status,
                    response=await response.text(),
                )
