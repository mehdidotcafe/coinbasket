from dataclasses import asdict
from unittest import mock
from pytest import fixture
from data_agent.similarity.similarity_document import SimilarityDocument
from data_agent.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from data_agent.ingestion.data_source.infrastructure.bsc.coingecko_tokens_data_source import (
    CoingeckoTokenListDataSource,
    Response,
)
from protocol.token import Token


@fixture
def http_request():
    return mock.Mock(spec=RequestsHttpRequest)


def test_coingecko_tokens_data_source_get(http_request: RequestsHttpRequest[Response]):
    http_request.get.return_value = {
        "tokens": [
            {
                "chainId": 56,
                "address": "0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93",
                "name": "Lithosphere",
                "symbol": "LITHO",
                "decimals": 18,
                "logoURI": "https://assets.coingecko.com/coins/images/21128/thumb/6gizpBLn.png?1696520507",
            }
        ]
    }

    # Create an instance of the data source with the mocked HttpRequest
    data_source = CoingeckoTokenListDataSource(http_request)

    # Call the get method and check the result
    similarity_documents = data_source.get()

    assert similarity_documents == [
        SimilarityDocument(
            metadata={
                "source": asdict(
                    Token(
                        name="Lithosphere",
                        display_name="Lithosphere",
                        ticker="LITHO",
                        address="0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93",
                    )
                ),
                "type": "token",
            },
            page_content="""
name: Lithosphere
display_name: Lithosphere
ticker: LITHO
address: 0x61909950e1bfb5d567c5463cbd33dc1cdc85ee93
""",
            id=None,
        ),
    ]

    http_request.get.assert_called_once_with(
        {
            "url": "https://tokens.coingecko.com/binance-smart-chain/all.json",
            "headers": {
                "accept": "application/json",
            },
        }
    )


def test_coingecko_tokens_data_source_version(
    http_request: RequestsHttpRequest[Response],
):
    data_source = CoingeckoTokenListDataSource(http_request)
    version = data_source.version()

    assert version == 1
