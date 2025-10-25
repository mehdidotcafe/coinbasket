import asyncio
from dataclasses import dataclass
from decimal import Decimal

from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from invest_agent.investment.exchange.exchange import Exchange

from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.order.order import Order
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.portfolio.holding.holding import Holding
from invest_agent.portfolio.posting.posting_repository import (
    PostingRepository,
)
from protocol.token import Token


@dataclass
class PortfolioBalance:
    native_balance: BalanceAtomic
    converted_balance: BalanceAtomic


@dataclass
class Portfolio:
    available_balance: PortfolioBalance
    holding_balances: list[PortfolioBalance]
    total_balance: BalanceAtomic[Token]
    pending_orders: list[Order]


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class GetPortfolioUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        posting_repository: PostingRepository,
        exchange: Exchange,
        chain: Chain,
        asset_balance_converter: AssetBalanceConverter,
    ):
        self.order_repository = order_repository
        self.posting_repository = posting_repository
        self.exchange = exchange
        self.chain = chain
        self.asset_balance_converter = asset_balance_converter

    async def execute(self, conversion_token: Token):
        conversion_token_decimals = await self.chain.get_token_decimals(
            conversion_token.address
        )
        holding_balances = await self.__fetch_holding_balances(conversion_token)
        available_balance = await self.__fetch_available_balance(conversion_token)

        return Portfolio(
            available_balance=available_balance,
            holding_balances=holding_balances,
            total_balance=self.__sum_balances_balances(
                [
                    available_balance.converted_balance,
                    *[balance.converted_balance for balance in holding_balances],
                ],
                conversion_token,
                conversion_token_decimals,
            ),
            pending_orders=await self.order_repository.get_pending_orders(),
        )

    async def __fetch_available_balance(self, conversion_token: Token):
        raw_available_balance = await self.chain.get_native_token_balance()

        converted_balance = await self.exchange.convert_balance_to_token(
            balance=raw_available_balance,
            token=conversion_token,
            investment_parameters=investment_parameters,
        )

        return PortfolioBalance(
            native_balance=converted_balance.sell_balance,
            converted_balance=converted_balance.buy_balance,
        )

    async def __fetch_holding_balances(self, conversion_token: Token):
        raw_holdings = await self.posting_repository.get_holding_balances()

        converted_balances = await asyncio.gather(
            *[
                self._convert_holding_balance_to_token(
                    holding=holding,
                    holdings=raw_holdings,
                    conversion_token=conversion_token,
                )
                for holding in raw_holdings
            ]
        )

        return converted_balances

    async def _convert_holding_balance_to_token(
        self,
        holding: Holding,
        holdings: list[Holding],
        conversion_token: Token,
    ) -> PortfolioBalance:
        converted_asset_balance = await self.asset_balance_converter.convert(
            sell_balance=holding.balance, buy_asset=conversion_token, holdings=holdings
        )

        return PortfolioBalance(
            native_balance=converted_asset_balance.total_balance.sell_balance,
            converted_balance=converted_asset_balance.total_balance.buy_balance,
        )

    def __sum_balances_balances(
        self,
        balances: list[BalanceAtomic],
        conversion_token: Token,
        conversion_token_decimals: int,
    ):
        return BalanceAtomic(
            asset=conversion_token,
            amount=sum(
                [balance.amount for balance in balances],
                Decimal(0),
            ),
            amount_atomic=sum([balance.amount_atomic for balance in balances]),
            decimals=conversion_token_decimals,
        )
