from api.address.address import Address
from api.investment.confirmed_order import ConfirmedOrder
from decimal import Decimal
import json
from api.database.infrastructure.sql_alchemy_base import Base
from api.database.infrastructure.sql_alchemy_base_repository import (
    NullableSession,
    SqlAlchemyBaseRepository,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from api.chain.balance import Balance, BalanceAtomic
from api.investment.order.confirmed_order_repository import ConfirmedOrderRepository


class ConfirmedOrderModel(Base):
    __tablename__ = "confirmed_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    planned_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("planned_orders.id")
    )
    address: Mapped[str] = mapped_column(String(42))

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[str] = mapped_column()
    buy_balance_amount: Mapped[str] = mapped_column()

    sell_balance_asset_id: Mapped[str] = mapped_column(String())
    sell_balance_asset: Mapped[str] = mapped_column()
    sell_balance_amount: Mapped[str] = mapped_column()

    def to_domain(self) -> ConfirmedOrder:
        return ConfirmedOrder(
            id=self.id,
            planned_order_id=self.planned_order_id,
            address=Address(self.address),
            buy_balance=Balance(
                asset=BalanceAtomic.deserialize_asset(self.buy_balance_asset),
                amount=Decimal(self.buy_balance_amount),
            ),
            sell_balance=Balance(
                asset=BalanceAtomic.deserialize_asset(self.sell_balance_asset),
                amount=Decimal(self.sell_balance_amount),
            ),
        )

    @staticmethod
    def from_domain(confirmed_order: ConfirmedOrder) -> "ConfirmedOrderModel":
        return ConfirmedOrderModel(
            id=confirmed_order.id,
            planned_order_id=confirmed_order.planned_order_id,
            address=str(confirmed_order.address),
            buy_balance_asset_id=confirmed_order.buy_balance.asset.id,
            buy_balance_asset=json.dumps(confirmed_order.buy_balance.asset.to_dict()),
            buy_balance_amount=format(confirmed_order.buy_balance.amount, "f"),
            sell_balance_asset_id=confirmed_order.sell_balance.asset.id,
            sell_balance_asset=json.dumps(confirmed_order.sell_balance.asset.to_dict()),
            sell_balance_amount=format(confirmed_order.sell_balance.amount, "f"),
        )


class SqlAlchemyConfirmedOrderRepository(
    ConfirmedOrderRepository, SqlAlchemyBaseRepository
):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def save(
        self, confirmed_order: ConfirmedOrder, session: NullableSession = None
    ) -> ConfirmedOrder:
        async with self.get_session(session) as session:
            session.add(ConfirmedOrderModel.from_domain(confirmed_order))
        return confirmed_order
