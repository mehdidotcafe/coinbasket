from typing import TYPE_CHECKING
from decimal import Decimal
import json
from invest_agent.database.infrastructure.sql_alchemy_base import Base

from invest_agent.portfolio.posting.posting import Posting, PostingType
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey, String, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import NUMERIC
from invest_agent.chain.balance import BalanceAtomic

if TYPE_CHECKING:
    from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
        TransactionModel,
    )


class PostingModel(Base):
    __tablename__ = "postings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)

    asset_id: Mapped[str] = mapped_column(String())
    asset: Mapped[str] = mapped_column()
    amount: Mapped[str] = mapped_column()
    amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    decimals: Mapped[int] = mapped_column()

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

    parent_posting_id: Mapped[str | None] = mapped_column(
        String(40),
        # No ForeignKey constraint because parent posting is created after child posting
        nullable=True
    )

    def to_domain(self) -> Posting:
        return Posting(
            id=self.id,
            transaction_id=self.transaction_id,
            asset_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.asset),
                amount=Decimal(self.amount),
                amount_atomic=int(self.amount_atomic),
                decimals=self.decimals,
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
            amount=format(posting.asset_balance.amount, "f"),
            amount_atomic=posting.asset_balance.amount_atomic,
            decimals=posting.asset_balance.decimals,
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

    async def get_holding_balances(self) -> list[BalanceAtomic]:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                result = await session.execute(self._get_default_holding_statement())
                rows = result.all()

                return [
                    BalanceAtomic(
                        asset=BalanceAtomic.deserialize_asset(asset_json),
                        amount=total_amount_atomic / Decimal(10**decimals),
                        amount_atomic=int(total_amount_atomic),
                        decimals=decimals,
                    )
                    for _asset_id, asset_json, decimals, total_amount_atomic in rows
                ]

    async def get_holding_balance(self, asset: Asset) -> BalanceAtomic:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                stmt = self._get_default_holding_statement().where(
                    PostingModel.asset_id == asset.id
                )
                result = await session.execute(stmt)
                rows = result.all()

                if not rows:
                    return BalanceAtomic(
                        asset=asset,
                        amount=Decimal(0),
                        amount_atomic=0,
                        decimals=0,
                    )

                asset_json = rows[0][1]
                decimals = rows[0][2]
                total_amount_atomic = rows[0][3]

                return BalanceAtomic(
                    asset=BalanceAtomic.deserialize_asset(asset_json),
                    amount=total_amount_atomic / Decimal(10**decimals),
                    amount_atomic=int(total_amount_atomic),
                    decimals=decimals,
                )

    def _get_default_holding_statement(self):
        return (
            select(
                PostingModel.asset_id,
                # Select any asset value of the same asset_id
                func.min(PostingModel.asset),
                func.min(PostingModel.decimals).label("decimals"),
                func.sum(PostingModel.amount_atomic).label("total_amount_atomic"),
            )
            .group_by(PostingModel.asset_id)
            .having(func.sum(PostingModel.amount_atomic) > 0)
        )
