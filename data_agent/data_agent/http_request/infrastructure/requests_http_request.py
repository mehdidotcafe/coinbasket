from typing import Generic, TypeVar
import requests

from data_agent.http_request.exceptions.failed_request_exception import (
    FailedRequestException,
)
from data_agent.http_request.http_request import GetParams, HttpRequest


T = TypeVar("T")


class RequestsHttpRequest(HttpRequest[T], Generic[T]):
    def get(self, params: GetParams) -> T:
        """
        Fetches data from a given URL using the requests library.
        """
        response = requests.get(
            params.get("url"), params.get("params"), headers=params.get("headers")
        )
        if response.status_code >= 200 and response.status_code < 400:
            return response.json()
        else:
            raise FailedRequestException(
                status_code=response.status_code,
                response=response.text,
            )
