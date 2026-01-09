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
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import (
    HoldingRepository,
)
from api.address.address import Address
from api.portfolio.small_balance.small_balance_policy import SmallBalancePolicy
from api.protocol.asset import Asset
from api.protocol.fixture.token import usdt_token


@dataclass
class PortfolioBalance:
    native_balance: BalanceAtomic
    converted_balance: BalanceAtomic


@dataclass
class Portfolio:
    available_balance: PortfolioBalance
    holding_balances: list[PortfolioBalance]
    total_balance: BalanceAtomic[Asset]
    pending_orders: list[Any]


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class GetPortfolioUseCase:
    def __init__(
        self,
        holding_repository: HoldingRepository,
        exchange: Exchange,
        chain: Chain,
        asset_balance_converter: AssetBalanceConverter,
        small_balance_policy: SmallBalancePolicy,
    ):
        self.holding_repository = holding_repository
        self.exchange = exchange
        self.chain = chain
        self.asset_balance_converter = asset_balance_converter
        self.small_balance_policy = small_balance_policy

    async def execute(self, address: Address, conversion_asset: Asset):
        holding_balances = await self.__fetch_holding_balances(
            address, conversion_asset
        )
        available_balance = await self.__fetch_available_balance(
            address, conversion_asset
        )

        return Portfolio(
            available_balance=available_balance,
            holding_balances=holding_balances,
            total_balance=self.__sum_balances_balances(
                [
                    available_balance.converted_balance,
                    *[balance.converted_balance for balance in holding_balances],
                ],
                conversion_asset,
            ),
            pending_orders=[],
        )

    async def __fetch_available_balance(
        self, address: Address, conversion_asset: Asset
    ):
        raw_available_balance = await self.chain.get_native_token_balance(
            address=address
        )

        converted_balance = await self.exchange.convert_balance_to_asset(
            taker=address,
            balance=raw_available_balance,
            asset=conversion_asset,
            investment_parameters=investment_parameters,
        )

        return PortfolioBalance(
            native_balance=converted_balance.sell_balance,
            converted_balance=converted_balance.buy_balance,
        )

    async def __fetch_holding_balances(self, address: Address, conversion_asset: Asset):
        raw_holdings = await self.holding_repository.get_holding_balances(address, [])

        tasks: list[CoroutineType[Any, Any, BalanceAtomic | PortfolioBalance]] = [
            self._compute_conversion_token_usd_rate(
                address, conversion_asset, raw_holdings
            )
        ]

        for holding in raw_holdings:
            tasks.append(
                self._convert_holding_balance_to_token(
                    address=address,
                    holding=holding,
                    holdings=raw_holdings,
                    conversion_asset=conversion_asset,
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
        address: Address,
        holding: Holding,
        holdings: list[Holding],
        conversion_asset: Asset,
    ) -> PortfolioBalance:
        converted_asset_balance = await self.asset_balance_converter.convert(
            taker=address,
            sell_balance=holding.balance,
            buy_asset=conversion_asset,
        )

        return PortfolioBalance(
            native_balance=converted_asset_balance.total_balance.sell_balance,
            converted_balance=converted_asset_balance.total_balance.buy_balance,
        )

    async def _compute_conversion_token_usd_rate(
        self, address: Address, conversion_asset: Asset, holdings: list[Holding]
    ):
        conversion_asset_decimals = conversion_asset.decimals
        sell_balance = BalanceAtomic(
            asset=conversion_asset,
            amount=Decimal("1.0"),
            amount_atomic=1 * 10**conversion_asset_decimals,
            decimals=conversion_asset_decimals,
        )

        if conversion_asset == usdt_token:
            return sell_balance

        converted_balance = await self.asset_balance_converter.convert(
            taker=address,
            sell_balance=sell_balance,
            buy_asset=usdt_token,
        )

        return converted_balance.total_balance.buy_balance

    def __sum_balances_balances(
        self,
        balances: list[BalanceAtomic],
        conversion_asset: Asset,
    ):
        return BalanceAtomic(
            asset=conversion_asset,
            amount=sum(
                [balance.amount for balance in balances],
                Decimal(0),
            ),
            amount_atomic=sum([balance.amount_atomic for balance in balances]),
            decimals=conversion_asset.decimals,
        )
