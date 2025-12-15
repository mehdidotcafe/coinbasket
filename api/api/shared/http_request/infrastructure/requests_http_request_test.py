from pytest import fixture
from api.shared.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)


@fixture
def http_request() -> RequestsHttpRequest:
    """
    Fixture to provide an instance of RequestsHttpRequest.
    """
    return RequestsHttpRequest()


def test_requests_http_request_defined(http_request: RequestsHttpRequest):
    """
    Test to ensure that the RequestsHttpRequest class is defined.
    """
    assert http_request is not None
    assert isinstance(http_request, RequestsHttpRequest)
