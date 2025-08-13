from typing import TYPE_CHECKING
from decimal import Decimal
import json
from typing import cast
from invest_agent.database.infrastructure.sql_alchemy_base import Base

from invest_agent.portfolio.posting import Posting, PostingType
from invest_agent.portfolio.posting_repository import PostingRepository
from protocol.token import Token
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import NUMERIC
from invest_agent.chain.balance import BalanceAtomic

if TYPE_CHECKING:
    from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
        TransactionModel,
    )


class PostingModel(Base):
    __tablename__ = "postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    asset_id: Mapped[str] = mapped_column(String())
    asset: Mapped[str] = mapped_column()
    amount: Mapped[str] = mapped_column()
    amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))

    transaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id")
    )
    created_at: Mapped[int] = mapped_column()
    type: Mapped[PostingType] = mapped_column()
    basket_id: Mapped[str | None] = mapped_column(String(), nullable=True)

    transaction: Mapped["TransactionModel"] = relationship(
        "TransactionModel",
        back_populates="postings",
    )

    def to_domain(self) -> Posting:
        return Posting(
            id=self.id,
            transaction_id=self.transaction_id,
            asset_balance=BalanceAtomic(
                asset=cast(Token, BalanceAtomic.deserialize_asset(self.asset)),
                amount=Decimal(self.amount),
                amount_atomic=int(self.amount_atomic),
            ),
            type=self.type,
            created_at=self.created_at,
            basket_id=self.basket_id,
        )

    @staticmethod
    def from_domain(posting: Posting) -> "PostingModel":
        return PostingModel(
            id=posting.id,
            transaction_id=posting.transaction_id,
            asset_id=posting.asset_balance.asset.id,
            asset=json.dumps(posting.asset_balance.asset.to_dict()),
            amount=str(posting.asset_balance.amount),
            amount_atomic=posting.asset_balance.amount_atomic,
            created_at=posting.created_at,
            type=posting.type,
            basket_id=posting.basket_id,
        )


class SqlAlchemyPostingRepository(PostingRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_posting(self, posting: Posting) -> Posting:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                session.add(PostingModel.from_domain(posting))
        return posting
