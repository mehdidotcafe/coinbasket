import asyncio
from dataclasses import dataclass
from decimal import Decimal
from types import CoroutineType
from typing import Any, cast

from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from api.investment.exchange.exchange import Exchange

from api.investment.investment_parameters import InvestmentParameters
from api.investment.order.order import Order
from api.investment.order.order_repository import OrderRepository
from api.portfolio.holding.holding import Holding
from api.portfolio.posting.posting_repository import (
    PostingRepository,
)
from api.portfolio.small_balance.small_balance_policy import SmallBalancePolicy
from protocol.token import Token
from protocol.fixture.token import usdt_token


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
        small_balance_policy: SmallBalancePolicy,
    ):
        self.order_repository = order_repository
        self.posting_repository = posting_repository
        self.exchange = exchange
        self.chain = chain
        self.asset_balance_converter = asset_balance_converter
        self.small_balance_policy = small_balance_policy

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

        tasks: list[CoroutineType[Any, Any, BalanceAtomic | PortfolioBalance]] = [
            self._compute_conversion_token_usd_rate(conversion_token, raw_holdings)
        ]

        for holding in raw_holdings:
            tasks.append(
                self._convert_holding_balance_to_token(
                    holding=holding,
                    holdings=raw_holdings,
                    conversion_token=conversion_token,
                )
            )

        conversion_token_usd_balance, *converted_balances = await asyncio.gather(*tasks)

        return [
            balance
            for balance in cast(list[PortfolioBalance], converted_balances)
            if not self.small_balance_policy.is_small_balance(
                balance.converted_balance,
                cast(BalanceAtomic, conversion_token_usd_balance),
            )
        ]

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

    async def _compute_conversion_token_usd_rate(
        self, conversion_token: Token, holdings: list[Holding]
    ):
        conversion_token_decimals = await self.chain.get_token_decimals(
            conversion_token.address
        )

        sell_balance = BalanceAtomic(
            asset=conversion_token,
            amount=Decimal("1.0"),
            amount_atomic=1 * 10**conversion_token_decimals,
            decimals=conversion_token_decimals,
        )

        if conversion_token == usdt_token:
            return sell_balance

        converted_balance = await self.asset_balance_converter.convert(
            sell_balance=sell_balance,
            buy_asset=usdt_token,
            holdings=holdings,
        )

        return converted_balance.total_balance.buy_balance

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
