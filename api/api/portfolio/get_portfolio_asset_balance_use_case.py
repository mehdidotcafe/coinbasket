from dataclasses import dataclass
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset


@dataclass
class PortfolioAssetBalance:
    holding_balance: BalanceAtomic
    available_balance: BalanceAtomic[Asset] | None = None


class GetPortfolioAssetBalanceUseCase:
    def __init__(
        self,
        chain: Chain,
        posting_repository: PostingRepository,
    ):
        self.chain = chain
        self.posting_repository = posting_repository

    async def execute(self, asset: Asset) -> PortfolioAssetBalance:
        asset_decimals = await self.chain.get_token_decimals(
            asset.get_pricing_token().address
        )

        if self.chain.is_native_token(asset) or self.chain.is_wrapped_native_token(
            asset
        ):
            holding = await self.posting_repository.get_holding_balance(
                self.chain.get_wrapped_base_token(), asset_decimals
            )
            return PortfolioAssetBalance(
                available_balance=await self.chain.get_native_token_balance(),
                holding_balance=holding.balance,
            )

        holding = await self.posting_repository.get_holding_balance(
            asset, asset_decimals
        )

        return PortfolioAssetBalance(holding_balance=holding.balance)
