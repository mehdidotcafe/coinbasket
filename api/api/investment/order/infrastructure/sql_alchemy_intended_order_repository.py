from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.investment.intended_order import IntendedOrder, IntendedOrderType
from decimal import Decimal
import json
from api.database.infrastructure.sql_alchemy_base import Base
from api.database.infrastructure.sql_alchemy_base_repository import (
    NullableSession,
    SqlAlchemyBaseRepository,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from api.investment.order.intended_order_repository import IntendedOrderRepository


class IntendedOrderModel(Base):
    __tablename__ = "intended_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    address: Mapped[str] = mapped_column(String(42))
    type: Mapped[IntendedOrderType] = mapped_column(String(4))

    sell_asset: Mapped[str | None] = mapped_column(nullable=True)
    buy_asset: Mapped[str | None] = mapped_column(nullable=True)
    amount: Mapped[str | None] = mapped_column(nullable=True)

    def to_domain(self) -> IntendedOrder:
        return IntendedOrder(
            id=self.id,
            address=Address(self.address),
            type=self.type,
            sell_asset=BalanceAtomic.deserialize_asset(self.sell_asset)
            if self.sell_asset
            else None,
            buy_asset=BalanceAtomic.deserialize_asset(self.buy_asset)
            if self.buy_asset
            else None,
            amount=Decimal(self.amount) if self.amount else None,
        )

    @staticmethod
    def from_domain(intended_order: IntendedOrder) -> "IntendedOrderModel":
        return IntendedOrderModel(
            id=intended_order.id,
            address=str(intended_order.address),
            type=intended_order.type,
            sell_asset=json.dumps(intended_order.sell_asset.to_dict())
            if intended_order.sell_asset
            else None,
            buy_asset=json.dumps(intended_order.buy_asset.to_dict())
            if intended_order.buy_asset
            else None,
            amount=format(intended_order.amount, "f")
            if intended_order.amount is not None
            else None,
        )


class SqlAlchemyIntendedOrderRepository(
    IntendedOrderRepository, SqlAlchemyBaseRepository
):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def save(
        self, intended_order: IntendedOrder, session: NullableSession = None
    ) -> IntendedOrder:
        async with self.get_session(session) as session:
            session.add(IntendedOrderModel.from_domain(intended_order))
        return intended_order
