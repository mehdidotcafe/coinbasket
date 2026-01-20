from decimal import Decimal
from api.address.address import Address
from api.protocol.asset import Asset
from attr import dataclass
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedBalance,
)


@dataclass
class AssetSwapPriceInfo:
    sell_asset: Asset
    sell_asset_amount: Decimal
    buy_asset: Asset


class GetAssetSwapPriceUseCase:
    """Use case for getting the swap price of a pair of assets. Basket against basket is not supported"""

    def __init__(
        self,
        chain: Chain,
        asset_balance_converter: AssetBalanceConverter,
    ):
        self.chain = chain
        self.asset_balance_converter = asset_balance_converter

    async def execute(
        self, address: Address, asset_swap_price_info: AssetSwapPriceInfo
    ) -> ConvertedBalance:
        decimals = asset_swap_price_info.sell_asset.decimals
        amount_atomic = int(asset_swap_price_info.sell_asset_amount * (10**decimals))

        converted_asset_balance = await self.asset_balance_converter.convert(
            taker=address,
            sell_balance=BalanceAtomic(
                asset=asset_swap_price_info.sell_asset,
                amount=asset_swap_price_info.sell_asset_amount,
                amount_atomic=amount_atomic,
                decimals=decimals,
            ),
            buy_asset=asset_swap_price_info.buy_asset,
        )

        return converted_asset_balance.total_balance
