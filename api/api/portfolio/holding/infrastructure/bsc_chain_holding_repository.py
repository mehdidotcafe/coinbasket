import asyncio
from api.address.address import Address
from api.chain.chain import Chain
from api.portfolio.holding.holding import Holding
from api.portfolio.holding.holding_repository import HoldingRepository
from api.protocol.asset import Asset


class BscChainHoldingRepository(HoldingRepository):
    def __init__(self, chain: Chain):
        self.chain = chain

    async def get_holding_balances(
        self,
        address: Address,
        assets: list[Asset],
    ) -> list[Holding]:
        holdings = await asyncio.gather(
            *[self.get_holding_balance(address, asset) for asset in assets]
        )

        return holdings

    async def get_holding_balance(
        self,
        address: Address,
        asset: Asset,
    ) -> Holding:
        return Holding(
            balance=await self.chain.get_token_balance(address, asset),
            children=None,
        )
