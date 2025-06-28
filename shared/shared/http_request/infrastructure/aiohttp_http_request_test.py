from pytest import fixture

from shared.http_request.infrastructure.aiohttp_http_request import AiohttpHttpRequest


@fixture
def http_request() -> AiohttpHttpRequest:
    """
    Fixture to provide an instance of AiohttpHttpRequest.
    """
    return AiohttpHttpRequest()


def test_aiohttp_http_request_defined(http_request: AiohttpHttpRequest):
    """
    Test to ensure that the AiohttpHttpRequest class is defined.
    """
    assert http_request is not None
    assert isinstance(http_request, AiohttpHttpRequest)
