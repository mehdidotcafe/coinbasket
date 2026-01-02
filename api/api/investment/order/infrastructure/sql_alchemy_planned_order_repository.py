from api.address.address import Address
from api.investment.planned_order import PlannedOrder
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
from api.chain.balance import BalanceAtomic
from api.investment.order.planned_order_repository import PlannedOrderRepository
from api.investment.planned_order import PlannedOrderBalance


class PlannedOrderModel(Base):
    __tablename__ = "planned_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    address: Mapped[str] = mapped_column(String(42))

    buy_asset_with_amount_asset_id: Mapped[str] = mapped_column(String())
    buy_asset_with_amount_asset: Mapped[str] = mapped_column()
    buy_asset_with_amount_available_amount: Mapped[str] = mapped_column()
    buy_asset_with_amount_amount: Mapped[str | None] = mapped_column(nullable=True)

    sell_asset_with_amount_asset_id: Mapped[str] = mapped_column(String())
    sell_asset_with_amount_asset: Mapped[str] = mapped_column()
    sell_asset_with_amount_available_amount: Mapped[str] = mapped_column()
    sell_asset_with_amount_amount: Mapped[str | None] = mapped_column(nullable=True)

    def to_domain(self) -> PlannedOrder:
        return PlannedOrder(
            id=self.id,
            address=Address(self.address),
            buy_asset_with_amount=PlannedOrderBalance(
                asset=BalanceAtomic.deserialize_asset(self.buy_asset_with_amount_asset),
                available_amount=Decimal(self.buy_asset_with_amount_available_amount),
                amount=Decimal(self.buy_asset_with_amount_amount)
                if self.buy_asset_with_amount_amount
                else None,
            ),
            sell_asset_with_amount=PlannedOrderBalance(
                asset=BalanceAtomic.deserialize_asset(
                    self.sell_asset_with_amount_asset
                ),
                available_amount=Decimal(self.sell_asset_with_amount_available_amount),
                amount=Decimal(self.sell_asset_with_amount_amount)
                if self.sell_asset_with_amount_amount
                else None,
            ),
        )

    @staticmethod
    def from_domain(planned_order: PlannedOrder) -> "PlannedOrderModel":
        return PlannedOrderModel(
            id=planned_order.id,
            address=str(planned_order.address),
            buy_asset_with_amount_asset_id=planned_order.buy_asset_with_amount.asset.id,
            buy_asset_with_amount_asset=json.dumps(
                planned_order.buy_asset_with_amount.asset.to_dict()
            ),
            buy_asset_with_amount_available_amount=format(
                planned_order.buy_asset_with_amount.available_amount, "f"
            ),
            buy_asset_with_amount_amount=format(
                planned_order.buy_asset_with_amount.amount, "f"
            )
            if planned_order.buy_asset_with_amount.amount is not None
            else None,
            sell_asset_with_amount_asset_id=planned_order.sell_asset_with_amount.asset.id,
            sell_asset_with_amount_asset=json.dumps(
                planned_order.sell_asset_with_amount.asset.to_dict()
            ),
            sell_asset_with_amount_available_amount=format(
                planned_order.sell_asset_with_amount.available_amount, "f"
            ),
            sell_asset_with_amount_amount=format(
                planned_order.sell_asset_with_amount.amount, "f"
            )
            if planned_order.sell_asset_with_amount.amount is not None
            else None,
        )


class SqlAlchemyPlannedOrderRepository(
    PlannedOrderRepository, SqlAlchemyBaseRepository
):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def save(
        self, planned_order: PlannedOrder, session: NullableSession = None
    ) -> PlannedOrder:
        async with self.get_session(session) as session:
            session.add(PlannedOrderModel.from_domain(planned_order))
        return planned_order
