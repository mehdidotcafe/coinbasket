from decimal import Decimal
from typing import Any, TypedDict
from invest_agent.http_request.http_request import HttpRequest
from invest_agent.investment.infrastructure.zero_x.price import Price
from invest_agent.investment.infrastructure.zero_x.quote import QuoteResult
from invest_agent.investment.investment_parameters import InvestmentParameters


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
        investment_parameters: InvestmentParameters,
        sell_entire_balance: bool | None = None,
        slippage_bps: Decimal | None = None,
    ) -> Price:
        url = f"{self.api_url}/swap/permit2/price"
        params = self.__make_params(
            chain_id,
            sell_token,
            buy_token,
            amount,
            taker,
            investment_parameters,
            sell_entire_balance,
            slippage_bps,
        )

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
        investment_parameters: InvestmentParameters,
        sell_entire_balance: bool | None = None,
        slippage_bps: Decimal | None = None,
    ) -> QuoteResult:
        url = f"{self.api_url}/swap/permit2/quote"
        params = self.__make_params(
            chain_id,
            sell_token,
            buy_token,
            amount,
            taker,
            investment_parameters,
            sell_entire_balance,
            slippage_bps,
        )

        return self.http_request.get(
            {
                "url": url,
                "params": params,
                "headers": self.default_headers,
            },
            QuoteResult,
        )

    def __make_params(
        self,
        chain_id: int,
        sell_token: str,
        buy_token: str,
        amount: int,
        taker: str,
        investment_parameters: InvestmentParameters,
        sell_entire_balance: bool | None = None,
        slippage_bps: Decimal | None = None,
    ) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            "chainId": chain_id,
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": amount,
            "taker": taker,
        }

        if sell_entire_balance is not None:
            params["sellEntireBalance"] = "true" if sell_entire_balance else "false"

        if slippage_bps is not None:
            params["slippageBps"] = int(slippage_bps)

        if investment_parameters.integrator_fee is not None:
            params["swapFeeRecipient"] = investment_parameters.integrator_fee.recipient
            params["swapFeeBps"] = int(
                self.__percentage_to_bps(
                    investment_parameters.integrator_fee.value_in_percentage
                )
            )
            params["swapFeeToken"] = investment_parameters.integrator_fee.token.address

        return params

    def __percentage_to_bps(self, percentage: Decimal) -> Decimal:
        return percentage * 100
