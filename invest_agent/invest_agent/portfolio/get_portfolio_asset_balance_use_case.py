from dataclasses import dataclass
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from protocol.token import Token


@dataclass
class PortfolioAssetBalance:
    holding_balance: BalanceAtomic | None = None
    available_balance: BalanceAtomic[Token] | None = None


class GetPortfolioAssetBalanceUseCase:
    def __init__(
        self,
        chain: Chain,
        posting_repository: PostingRepository,
    ):
        self.chain = chain
        self.posting_repository = posting_repository

    async def execute(self, token: Token) -> PortfolioAssetBalance:
        if self.chain.is_native_token(token) or self.chain.is_wrapped_native_token(
            token
        ):
            holding = await self.posting_repository.get_holding_balance(
                self.chain.get_wrapped_base_token()
            )
            return PortfolioAssetBalance(
                available_balance=await self.chain.get_native_token_balance(),
                holding_balance=holding.balance if holding else None,
            )

        holding = await self.posting_repository.get_holding_balance(
            self.chain.get_wrapped_base_token()
        )

        return PortfolioAssetBalance(holding_balance=holding.balance if holding else None)
