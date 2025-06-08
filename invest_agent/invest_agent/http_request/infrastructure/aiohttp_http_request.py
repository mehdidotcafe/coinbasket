from typing import Generic, TypeVar
from pydantic import BaseModel
import aiohttp

from invest_agent.http_request.exception.failed_request import (
    FailedRequest,
)
from invest_agent.http_request.http_request import GetParams, HttpRequest, PostParams


T = TypeVar("T", bound=BaseModel)


class AiohttpHttpRequest(HttpRequest[T], Generic[T]):
    TIMEOUT = 20  # seconds

    async def get(self, params: GetParams, schema: T) -> T:
        """
        Fetches data from a given URL using the aiohttp library.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                params.get("url"),
                params=params.get("params"),
                headers=params.get("headers"),
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as response:
                if response.status >= 200 and response.status < 400:
                    return schema.model_validate(await response.json())
                else:
                    print(f"Failed request: {response.status} {await response.text()}")

                    raise FailedRequest(
                        status_code=response.status,
                        response=await response.text(),
                    )

    async def post(self, params: PostParams, schema: T) -> T:
        """
        Sends a POST request to a given URL using the aiohttp library.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                params.get("url"),
                json=params.get("body"),
                headers=params.get("headers"),
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as response:
                if response.status >= 200 and response.status < 400:
                    print(f"Response: {await response.json()}")
                    return schema.model_validate(await response.json())
                else:
                    raise FailedRequest(
                        status_code=response.status,
                        response=await response.text(),
                    )
