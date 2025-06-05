from typing import Generic, TypeVar
from pydantic import BaseModel
import requests

from invest_agent.http_request.exception.failed_request import (
    FailedRequest,
)
from invest_agent.http_request.http_request import GetParams, HttpRequest, PostParams


T = TypeVar("T", bound=BaseModel)


class RequestsHttpRequest(HttpRequest[T], Generic[T]):
    TIMEOUT = 20  # seconds

    def get(self, params: GetParams, schema: T) -> T:
        """
        Fetches data from a given URL using the requests library.
        """
        response = requests.get(
            params.get("url"),
            params.get("params"),
            headers=params.get("headers"),
            timeout=self.TIMEOUT,
        )
        if response.status_code >= 200 and response.status_code < 400:
            return schema.model_validate(response.json())
        else:
            print(f"Failed request: {response.status_code} {response.text}")

            raise FailedRequest(
                status_code=response.status_code,
                response=response.text,
            )

    def post(self, params: PostParams, schema: T) -> T:
        """
        Sends a POST request to a given URL using the requests library.
        """
        response = requests.post(
            params.get("url"),
            json=params.get("body"),
            headers=params.get("headers"),
            timeout=self.TIMEOUT,
        )
        if response.status_code >= 200 and response.status_code < 400:
            print(f"Response: {response.json()}")
            return schema.model_validate(response.json())
        else:
            raise FailedRequest(
                status_code=response.status_code,
                response=response.text,
            )
