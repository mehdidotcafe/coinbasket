from dataclasses import dataclass
from decimal import Decimal
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.exchange.exchange import Exchange
from api.investment.investment_parameters import InvestmentParameters
from api.protocol.asset import Asset


@dataclass
class ConvertedBalance:
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic


@dataclass
class ConvertedAssetBalance:
    total_balance: ConvertedBalance
    balances: list[ConvertedBalance]


class AssetBalanceConverter:
    def __init__(self, exchange: Exchange, chain: Chain):
        self.exchange = exchange
        self.chain = chain

    async def convert(
        self,
        taker: Address,
        sell_balance: BalanceAtomic,
        buy_asset: Asset,
    ) -> ConvertedAssetBalance:
        return await self._convert_sell_asset_to_buy_asset(
            taker,
            sell_balance,
            buy_asset,
        )

    async def _convert_sell_asset_to_buy_asset(
        self,
        taker: Address,
        sell_balance: BalanceAtomic[Asset],
        buy_asset: Asset,
    ) -> ConvertedAssetBalance:
        result = await self.exchange.convert_balance_to_asset(
            taker=taker,
            balance=sell_balance,
            asset=buy_asset,
            investment_parameters=InvestmentParameters(
                slippage_tolerance_in_percentage=Decimal("1"),
            ),
        )
        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=result.sell_balance,
                buy_balance=result.buy_balance,
            ),
            balances=[],
        )

    async def _build_empty_balance(
        self, sell_balance: BalanceAtomic, buy_asset: Asset
    ) -> ConvertedAssetBalance:
        buy_asset_decimals = await self.chain.get_token_decimals(buy_asset.address)
        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=sell_balance,
                buy_balance=BalanceAtomic.empty(
                    asset=buy_asset, decimals=buy_asset_decimals
                ),
            ),
            balances=[],
        )
