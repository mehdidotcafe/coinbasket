from dataclasses import dataclass
from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain
from api.portfolio.holding.holding_repository import HoldingRepository
from api.protocol.asset import Asset


@dataclass
class PortfolioAssetBalance:
    holding_balance: BalanceAtomic
    available_balance: BalanceAtomic[Asset] | None = None


class GetPortfolioAssetBalanceUseCase:
    def __init__(
        self,
        chain: Chain,
        holding_repository: HoldingRepository,
    ):
        self.chain = chain
        self.holding_repository = holding_repository

    async def execute(self, address: Address, asset: Asset) -> PortfolioAssetBalance:
        if self.chain.is_native_token(asset) or self.chain.is_wrapped_native_token(
            asset
        ):
            holding = await self.holding_repository.get_holding_balance(
                address, self.chain.get_wrapped_base_token()
            )
            return PortfolioAssetBalance(
                available_balance=await self.chain.get_native_token_balance(address),
                holding_balance=holding.balance,
            )

        holding = await self.holding_repository.get_holding_balance(address, asset)

        return PortfolioAssetBalance(holding_balance=holding.balance)
