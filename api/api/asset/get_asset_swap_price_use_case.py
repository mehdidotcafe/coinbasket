from decimal import Decimal
from attr import dataclass
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
    ConvertedBalance,
)
from api.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset


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
        posting_repository: PostingRepository,
        asset_balance_converter: AssetBalanceConverter,
    ):
        self.chain = chain
        self.posting_repository = posting_repository
        self.asset_balance_converter = asset_balance_converter

    async def execute(
        self, asset_swap_price_info: AssetSwapPriceInfo
    ) -> ConvertedBalance:
        sell_asset_decimals = await self.chain.get_token_decimals(
            asset_swap_price_info.sell_asset.get_pricing_token().address
        )

        holding = await self.posting_repository.get_holding_balance(
            asset_swap_price_info.sell_asset, sell_asset_decimals
        )
        pricing_sell_token = asset_swap_price_info.sell_asset.get_pricing_token()
        amount_atomic, decimals = await self.chain.convert_amount_to_amount_atomic(
            token=pricing_sell_token,
            amount_readable=asset_swap_price_info.sell_asset_amount,
        )

        converted_asset_balance = await self.asset_balance_converter.convert(
            sell_balance=BalanceAtomic(
                asset=asset_swap_price_info.sell_asset,
                amount=asset_swap_price_info.sell_asset_amount,
                amount_atomic=amount_atomic,
                decimals=decimals,
            ),
            buy_asset=asset_swap_price_info.buy_asset,
            holdings=[holding],
        )

        return converted_asset_balance.total_balance
