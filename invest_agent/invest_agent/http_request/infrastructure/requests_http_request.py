from typing import Generic, TypeVar
from pydantic import BaseModel, VERSION
import requests

from invest_agent.http_request.exceptions.failed_request_exception import (
    FailedRequestException,
)
from invest_agent.http_request.http_request import GetParams, HttpRequest, PostParams


T = TypeVar("T", bound=BaseModel)


class RequestsHttpRequest(HttpRequest[T], Generic[T]):
    def get(self, params: GetParams, schema: T) -> T:
        """
        Fetches data from a given URL using the requests library.
        """
        response = requests.get(
            params.get("url"), params.get("params"), headers=params.get("headers")
        )
        if response.status_code >= 200 and response.status_code < 400:
            return schema.model_validate(response.json())
        else:
            print(f"Failed request: {response.status_code} {response.text}")

            raise FailedRequestException(
                status_code=response.status_code,
                response=response.text,
            )

    def post(self, params: PostParams, schema: T) -> T:
        """
        Sends a POST request to a given URL using the requests library.
        """
        response = requests.post(
            params.get("url"), json=params.get("body"), headers=params.get("headers")
        )
        if response.status_code >= 200 and response.status_code < 400:
            print(f"Response: {response.json()}")
            return schema.model_validate(response.json())
        else:
            raise FailedRequestException(
                status_code=response.status_code,
                response=response.text,
            )
