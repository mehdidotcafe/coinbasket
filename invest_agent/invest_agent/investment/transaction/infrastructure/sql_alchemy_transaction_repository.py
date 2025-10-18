from typing import TYPE_CHECKING, cast
from decimal import Decimal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.fees import Fees
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey, String, Integer, Text, select
from invest_agent.investment.transaction.transaction import (
    Transaction,
    TransactionTrigger,
    TransactionType,
)
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.database.infrastructure.sql_alchemy_base import Base
from invest_agent.database.infrastructure.sql_alchemy_base_repository import (
    NullableSession,
    SqlAlchemyBaseRepository,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import NUMERIC
import json


if TYPE_CHECKING:
    from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
        PostingModel,
    )
    from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
        OrderModel,
    )


class TransactionModel(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    sell_balance_asset_id: Mapped[str] = mapped_column(String())
    sell_balance_asset: Mapped[str] = mapped_column(Text)
    sell_balance_amount: Mapped[str] = mapped_column(String)
    sell_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    sell_balance_decimals: Mapped[int] = mapped_column()

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[str] = mapped_column(Text)
    buy_balance_amount: Mapped[str] = mapped_column(String)
    buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    buy_balance_decimals: Mapped[int] = mapped_column()

    executed_buy_balance_asset_id: Mapped[str] = mapped_column(String())
    executed_buy_balance_asset: Mapped[str] = mapped_column()
    executed_buy_balance_amount: Mapped[str] = mapped_column()
    executed_buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    executed_buy_balance_decimals: Mapped[int] = mapped_column()

    executed_sell_balance_asset_id: Mapped[str] = mapped_column(String())
    executed_sell_balance_asset: Mapped[str] = mapped_column()
    executed_sell_balance_amount: Mapped[str] = mapped_column()
    executed_sell_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    executed_sell_balance_decimals: Mapped[int] = mapped_column()

    type: Mapped[str] = mapped_column(String)
    created_at: Mapped[int] = mapped_column(Integer)
    transaction_hash: Mapped[str] = mapped_column(String, nullable=True)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"))
    trigger: Mapped[str] = mapped_column(String)
    fees: Mapped[str | None] = mapped_column(Text, nullable=True)
    basket_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    parent_transaction_id: Mapped[str | None] = mapped_column(
        String(36),
        # No ForeignKey constraint because parent transaction is created after child transactions
        nullable=True,
    )

    postings: Mapped[list["PostingModel"]] = relationship(
        "PostingModel",
        back_populates="transaction",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    order: Mapped["OrderModel"] = relationship(
        "OrderModel",
        back_populates="transactions",
    )

    @staticmethod
    def from_domain(transaction: Transaction) -> "TransactionModel":
        """Convert a Transaction domain object to a TransactionModel."""
        return TransactionModel(
            id=transaction.id,
            sell_balance_asset_id=transaction.sell_balance.asset.id,
            sell_balance_asset=json.dumps(transaction.sell_balance.asset.to_dict()),
            sell_balance_amount=format(transaction.sell_balance.amount, "f"),
            sell_balance_amount_atomic=transaction.sell_balance.amount_atomic,
            sell_balance_decimals=transaction.sell_balance.decimals,
            buy_balance_asset_id=transaction.buy_balance.asset.id,
            buy_balance_asset=json.dumps(transaction.buy_balance.asset.to_dict()),
            buy_balance_amount=format(transaction.buy_balance.amount, "f"),
            buy_balance_amount_atomic=transaction.buy_balance.amount_atomic,
            buy_balance_decimals=transaction.buy_balance.decimals,
            executed_sell_balance_asset_id=transaction.executed_sell_balance.asset.id,
            executed_sell_balance_asset=json.dumps(
                transaction.executed_sell_balance.asset.to_dict()
            ),
            executed_sell_balance_amount=format(
                transaction.executed_sell_balance.amount, "f"
            ),
            executed_sell_balance_amount_atomic=transaction.executed_sell_balance.amount_atomic,
            executed_sell_balance_decimals=transaction.executed_sell_balance.decimals,
            executed_buy_balance_asset_id=transaction.executed_buy_balance.asset.id,
            executed_buy_balance_asset=json.dumps(
                transaction.executed_buy_balance.asset.to_dict()
            ),
            executed_buy_balance_amount=format(
                transaction.executed_buy_balance.amount, "f"
            ),
            executed_buy_balance_amount_atomic=transaction.executed_buy_balance.amount_atomic,
            executed_buy_balance_decimals=transaction.executed_buy_balance.decimals,
            type=transaction.type,
            created_at=transaction.created_at,
            transaction_hash=transaction.transaction_hash,
            order_id=transaction.order_id,
            trigger=transaction.trigger,
            fees=transaction.fees.serialize() if transaction.fees else None,
            basket_id=transaction.basket_id,
            parent_transaction_id=transaction.parent_transaction_id,
            postings=[],
        )

    def to_domain(self) -> Transaction:
        """Convert a TransactionModel to a Transaction domain object."""
        return Transaction(
            id=self.id,
            sell_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.sell_balance_asset),
                amount=Decimal(self.sell_balance_amount),
                amount_atomic=int(self.sell_balance_amount_atomic),
                decimals=self.sell_balance_decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.buy_balance_asset),
                amount=Decimal(self.buy_balance_amount),
                amount_atomic=int(self.buy_balance_amount_atomic),
                decimals=self.buy_balance_decimals,
            ),
            executed_sell_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.executed_sell_balance_asset),
                amount=Decimal(self.executed_sell_balance_amount),
                amount_atomic=int(self.executed_sell_balance_amount_atomic),
                decimals=self.executed_sell_balance_decimals,
            ),
            executed_buy_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.executed_buy_balance_asset),
                amount=Decimal(self.executed_buy_balance_amount),
                amount_atomic=int(self.executed_buy_balance_amount_atomic),
                decimals=self.executed_buy_balance_decimals,
            ),
            type=cast(TransactionType, self.type),
            created_at=self.created_at,
            transaction_hash=self.transaction_hash,
            order_id=self.order_id,
            trigger=cast(TransactionTrigger, self.trigger),
            fees=Fees.deserialize(self.fees) if self.fees else None,
            basket_id=self.basket_id,
            parent_transaction_id=self.parent_transaction_id,
        )


class SqlAlchemyTransactionRepository(TransactionRepository, SqlAlchemyBaseRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_transaction(
        self, transaction: Transaction, session: NullableSession = None
    ) -> Transaction:
        async with self.get_session(session) as session:
            session.add(TransactionModel.from_domain(transaction))
        return transaction

    async def get_transactions(
        self, transaction_ids: list[str], session: NullableSession = None
    ) -> list[Transaction]:
        async with self.get_session(session) as session:
            stmt = select(TransactionModel).where(
                TransactionModel.id.in_(transaction_ids)
            )

            result = await session.execute(stmt)

            transaction_models = result.scalars().all()
            return [model.to_domain() for model in transaction_models]
