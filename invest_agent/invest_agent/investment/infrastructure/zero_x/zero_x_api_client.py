from typing import Any, TypedDict
from invest_agent.http_request.http_request import HttpRequest
from invest_agent.investment.infrastructure.zero_x.price import Price
from invest_agent.investment.infrastructure.zero_x.quote import Quote


class Configuration(TypedDict):
    zero_x_api_url: str
    zero_x_api_key: str


class ZeroXApiClient:
    def __init__(self, configuration: Configuration, http_request: HttpRequest[Any]):
        self.api_url = configuration["zero_x_api_url"]

        self.default_headers = {
            "Content-Type": "application/json",
            "0x-api-key": configuration["zero_x_api_key"],
            "0x-version": "v2",
        }

        self.http_request = http_request

    def get_price(
        self,
        taker: str,
        chain_id: int,
        sell_token: str,
        buy_token: str,
        amount: int,
    ) -> Price:
        url = f"{self.api_url}/swap/permit2/price"
        params: dict[str, str | int] = {
            "chainId": chain_id,
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": amount,
            "taker": taker,
        }

        return self.http_request.get(
            {
                "url": url,
                "params": params,
                "headers": self.default_headers,
            },
            Price,
        )

    def get_quote(
        self,
        taker: str,
        chain_id: int,
        sell_token: str,
        buy_token: str,
        amount: int,
    ) -> Quote:
        url = f"{self.api_url}/swap/permit2/quote"
        params: dict[str, str | int] = {
            "chainId": chain_id,
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": amount,
            "taker": taker,
        }

        return self.http_request.get(
            {
                "url": url,
                "params": params,
                "headers": self.default_headers,
            },
            Quote,
        )
