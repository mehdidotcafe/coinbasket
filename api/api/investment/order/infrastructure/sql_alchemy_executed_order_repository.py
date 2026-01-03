from typing import Any
from api.address.address import Address
from api.investment.executed_order import ExecutedOrder
from decimal import Decimal
from api.database.infrastructure.sql_alchemy_base import Base
from api.database.infrastructure.sql_alchemy_base_repository import (
    NullableSession,
    SqlAlchemyBaseRepository,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import NUMERIC, JSONB
from sqlalchemy.future import select
from api.chain.balance import BalanceAtomic
from api.investment.order.executed_order_repository import ExecutedOrderRepository
from api.protocol.asset import Asset
from api.protocol.basket import Basket
from api.protocol.token import Token


def _deserialize_asset_from_dict(asset_dict: dict[str, Any]) -> Asset:
    """Deserialize an asset from a dictionary."""

    def deserialize_asset(token: dict[str, Any]) -> Asset:
        ChildAsset = Token if token["type"] == "TOKEN" else Basket

        return ChildAsset(
            id=token["id"],
            name=token["name"],
            display_name=token["display_name"],
            ticker=token["ticker"],
            address=token["address"],
            decimals=token["decimals"],
            categories=token["categories"],
            description=token["description"],
        )

    return deserialize_asset(asset_dict)


class ExecutedOrderModel(Base):
    __tablename__ = "executed_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    signable_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("signable_orders.id")
    )
    transaction_hash: Mapped[str] = mapped_column(String(66))
    address: Mapped[str] = mapped_column(String(42))

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[dict[str, Any]] = mapped_column(JSONB)
    buy_balance_amount: Mapped[str] = mapped_column()
    buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    buy_balance_decimals: Mapped[int] = mapped_column()

    sell_balance_asset_id: Mapped[str] = mapped_column(String())
    sell_balance_asset: Mapped[dict[str, Any]] = mapped_column(JSONB)
    sell_balance_amount: Mapped[str] = mapped_column()
    sell_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    sell_balance_decimals: Mapped[int] = mapped_column()

    rate: Mapped[str | None] = mapped_column(nullable=True)

    def to_domain(self) -> ExecutedOrder:
        return ExecutedOrder(
            id=self.id,
            signable_order_id=self.signable_order_id,
            transaction_hash=self.transaction_hash,
            address=Address(self.address),
            buy_balance=BalanceAtomic(
                asset=_deserialize_asset_from_dict(self.buy_balance_asset),
                amount=Decimal(self.buy_balance_amount),
                amount_atomic=int(self.buy_balance_amount_atomic),
                decimals=self.buy_balance_decimals,
            ),
            sell_balance=BalanceAtomic(
                asset=_deserialize_asset_from_dict(self.sell_balance_asset),
                amount=Decimal(self.sell_balance_amount),
                amount_atomic=int(self.sell_balance_amount_atomic),
                decimals=self.sell_balance_decimals,
            ),
            rate=Decimal(self.rate) if self.rate else None,
        )

    @staticmethod
    def from_domain(executed_order: ExecutedOrder) -> "ExecutedOrderModel":
        return ExecutedOrderModel(
            id=executed_order.id,
            signable_order_id=executed_order.signable_order_id,
            transaction_hash=executed_order.transaction_hash,
            address=str(executed_order.address),
            buy_balance_asset_id=executed_order.buy_balance.asset.id,
            buy_balance_asset=executed_order.buy_balance.asset.to_dict(),
            buy_balance_amount=format(executed_order.buy_balance.amount, "f"),
            buy_balance_amount_atomic=executed_order.buy_balance.amount_atomic,
            buy_balance_decimals=executed_order.buy_balance.decimals,
            sell_balance_asset_id=executed_order.sell_balance.asset.id,
            sell_balance_asset=executed_order.sell_balance.asset.to_dict(),
            sell_balance_amount=format(executed_order.sell_balance.amount, "f"),
            sell_balance_amount_atomic=executed_order.sell_balance.amount_atomic,
            sell_balance_decimals=executed_order.sell_balance.decimals,
            rate=format(executed_order.rate, "f") if executed_order.rate else None,
        )


class SqlAlchemyExecutedOrderRepository(
    ExecutedOrderRepository, SqlAlchemyBaseRepository
):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def save(
        self, executed_order: ExecutedOrder, session: NullableSession = None
    ) -> ExecutedOrder:
        async with self.get_session(session) as session:
            session.add(ExecutedOrderModel.from_domain(executed_order))
        return executed_order

    async def get(
        self,
        limit: int | None = None,
        offset: int | None = None,
        session: NullableSession = None,
    ) -> list[ExecutedOrder]:
        async with self.get_session(session) as session:
            stmt = select(ExecutedOrderModel)
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            result = await session.execute(stmt)
            order_models = result.scalars().all()
            return [row.to_domain() for row in order_models]

    async def get_one(
        self, executed_order_id: str, session: NullableSession = None
    ) -> ExecutedOrder | None:
        async with self.get_session(session) as session:
            result = await session.get(ExecutedOrderModel, executed_order_id)
            if result:
                return result.to_domain()
            return None
