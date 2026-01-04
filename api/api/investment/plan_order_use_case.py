from decimal import Decimal
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from api.investment.exchange.exchange import Exchange
from api.investment.intended_order import IntendedOrder
from api.investment.investment_parameters import InvestmentParameters

from api.investment.planned_order import PlannedOrder, PlannedOrderBalance
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import HoldingRepository
from api.protocol.asset import Asset


class PlanOrderUseCase:
    def __init__(
        self,
        exchange: Exchange,
        chain: Chain,
        holding_repository: HoldingRepository,
        asset_balance_converter: AssetBalanceConverter,
    ):
        self.exchange = exchange
        self.chain = chain
        self.holding_repository = holding_repository
        self.asset_balance_converter = asset_balance_converter

    async def execute(
        self, address: Address, intended_order: IntendedOrder
    ) -> PlannedOrder | None:
        sell_asset = (
            intended_order.sell_asset_with_amount.asset
            if intended_order.sell_asset_with_amount
            else self.chain.get_base_token()
        )

        buy_asset = (
            intended_order.buy_asset_with_amount.asset
            if intended_order.buy_asset_with_amount
            else self.chain.get_base_token()
        )

        if sell_asset.address == buy_asset.address:
            return None

        holdings = await self.holding_repository.get_holding_balances(
            address,
            [
                sell_asset,
                buy_asset,
            ],
        )
        holding_balances = self._convert_holding_to_dict(holdings)

        sell_asset_available_amount = self._get_available_amount(
            holding_balances, sell_asset
        )

        buy_asset_available_amount = self._get_available_amount(
            holding_balances, buy_asset
        )

        if (
            intended_order.sell_asset_with_amount
            and intended_order.sell_asset_with_amount.amount
        ):
            (
                sell_balance_amount_atomic,
                sell_balance_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                asset=sell_asset,
                amount_readable=intended_order.sell_asset_with_amount.amount,
            )

            converted_asset_balance = await self.asset_balance_converter.convert(
                taker=address,
                sell_balance=BalanceAtomic[Asset](
                    asset=sell_asset,
                    amount=intended_order.sell_asset_with_amount.amount,
                    amount_atomic=sell_balance_amount_atomic,
                    decimals=sell_balance_decimals,
                ),
                buy_asset=buy_asset,
            )

            return PlannedOrder(
                id=intended_order.id,
                address=intended_order.address,
                sell_asset_with_amount=PlannedOrderBalance(
                    asset=sell_asset,
                    amount=converted_asset_balance.total_balance.sell_balance.amount,
                    available_amount=sell_asset_available_amount,
                ),
                buy_asset_with_amount=PlannedOrderBalance(
                    asset=buy_asset,
                    amount=converted_asset_balance.total_balance.buy_balance.amount,
                    available_amount=buy_asset_available_amount,
                ),
            )

        if (
            intended_order.buy_asset_with_amount
            and intended_order.buy_asset_with_amount.amount
        ):
            buy_asset_amount = intended_order.buy_asset_with_amount.amount

            (
                buy_balance_amount_atomic,
                buy_balance_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                asset=buy_asset,
                amount_readable=buy_asset_amount,
            )
            buy_balance = BalanceAtomic[Asset](
                asset=buy_asset,
                amount=buy_asset_amount,
                amount_atomic=buy_balance_amount_atomic,
                decimals=buy_balance_decimals,
            )

            # TODO: Flipping sell and buy token is inaccurate
            converted_balance = await self.exchange.convert_balance_to_asset(
                taker=address,
                balance=buy_balance,
                asset=sell_asset,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal(1)
                ),
            )

            return PlannedOrder(
                id=intended_order.id,
                address=intended_order.address,
                sell_asset_with_amount=PlannedOrderBalance(
                    asset=sell_asset,
                    amount=converted_balance.sell_balance.amount,
                    available_amount=sell_asset_available_amount,
                ),
                buy_asset_with_amount=PlannedOrderBalance(
                    asset=buy_asset,
                    amount=converted_balance.buy_balance.amount,
                    available_amount=buy_asset_available_amount,
                ),
            )

        if intended_order.sell_asset_with_amount:
            return PlannedOrder(
                id=intended_order.id,
                address=intended_order.address,
                sell_asset_with_amount=PlannedOrderBalance(
                    asset=sell_asset,
                    amount=intended_order.sell_asset_with_amount.amount
                    if intended_order.sell_asset_with_amount
                    else None,
                    available_amount=sell_asset_available_amount,
                ),
                buy_asset_with_amount=PlannedOrderBalance(
                    asset=buy_asset,
                    amount=None,
                    available_amount=buy_asset_available_amount,
                ),
            )

        if intended_order.buy_asset_with_amount:
            return PlannedOrder(
                id=intended_order.id,
                address=intended_order.address,
                sell_asset_with_amount=PlannedOrderBalance(
                    asset=sell_asset,
                    amount=None,
                    available_amount=sell_asset_available_amount,
                ),
                buy_asset_with_amount=PlannedOrderBalance(
                    asset=buy_asset,
                    amount=intended_order.buy_asset_with_amount.amount
                    if intended_order.buy_asset_with_amount
                    else None,
                    available_amount=buy_asset_available_amount,
                ),
            )

    def _get_available_amount(
        self, holding_balances_per_token: dict[str, BalanceAtomic], asset: Asset
    ) -> Decimal:
        holding_balance = holding_balances_per_token.get(asset.id)

        return holding_balance.amount if holding_balance else Decimal("0")

    def _convert_holding_to_dict(
        self, holdings: list[Holding]
    ) -> dict[str, BalanceAtomic]:
        holding_balances_per_token = {
            holding.balance.asset.id: holding.balance for holding in holdings
        }

        return holding_balances_per_token
