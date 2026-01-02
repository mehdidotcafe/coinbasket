from api.address.address import Address
from api.investment.intended_order import IntendedOrder
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
from api.investment.order.intended_order_repository import IntendedOrderRepository
from api.investment.intended_order import IntendedOrderBalance


class IntendedOrderModel(Base):
    __tablename__ = "intended_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    address: Mapped[str] = mapped_column(String(42))

    buy_asset_with_amount_asset_id: Mapped[str | None] = mapped_column(
        String(), nullable=True
    )
    buy_asset_with_amount_asset: Mapped[str | None] = mapped_column(nullable=True)
    buy_asset_with_amount_amount: Mapped[str | None] = mapped_column(nullable=True)

    sell_asset_with_amount_asset_id: Mapped[str | None] = mapped_column(
        String(), nullable=True
    )
    sell_asset_with_amount_asset: Mapped[str | None] = mapped_column(nullable=True)
    sell_asset_with_amount_amount: Mapped[str | None] = mapped_column(nullable=True)

    def to_domain(self) -> IntendedOrder:
        buy_asset_with_amount = None
        if self.buy_asset_with_amount_asset:
            buy_asset_with_amount = IntendedOrderBalance(
                asset=BalanceAtomic.deserialize_asset(self.buy_asset_with_amount_asset),
                amount=Decimal(self.buy_asset_with_amount_amount)
                if self.buy_asset_with_amount_amount
                else None,
            )

        sell_asset_with_amount = None
        if self.sell_asset_with_amount_asset:
            sell_asset_with_amount = IntendedOrderBalance(
                asset=BalanceAtomic.deserialize_asset(
                    self.sell_asset_with_amount_asset
                ),
                amount=Decimal(self.sell_asset_with_amount_amount)
                if self.sell_asset_with_amount_amount
                else None,
            )

        return IntendedOrder(
            id=self.id,
            address=Address(self.address),
            buy_asset_with_amount=buy_asset_with_amount,
            sell_asset_with_amount=sell_asset_with_amount,
        )

    @staticmethod
    def from_domain(intended_order: IntendedOrder) -> "IntendedOrderModel":
        buy_asset_id = None
        buy_asset_json = None
        buy_amount = None
        if intended_order.buy_asset_with_amount:
            buy_asset_id = intended_order.buy_asset_with_amount.asset.id
            buy_asset_json = json.dumps(
                intended_order.buy_asset_with_amount.asset.to_dict()
            )
            buy_amount = (
                format(intended_order.buy_asset_with_amount.amount, "f")
                if intended_order.buy_asset_with_amount.amount
                else None
            )

        sell_asset_id = None
        sell_asset_json = None
        sell_amount = None
        if intended_order.sell_asset_with_amount:
            sell_asset_id = intended_order.sell_asset_with_amount.asset.id
            sell_asset_json = json.dumps(
                intended_order.sell_asset_with_amount.asset.to_dict()
            )
            sell_amount = (
                format(intended_order.sell_asset_with_amount.amount, "f")
                if intended_order.sell_asset_with_amount.amount
                else None
            )

        return IntendedOrderModel(
            id=intended_order.id,
            address=str(intended_order.address),
            buy_asset_with_amount_asset_id=buy_asset_id,
            buy_asset_with_amount_asset=buy_asset_json,
            buy_asset_with_amount_amount=buy_amount,
            sell_asset_with_amount_asset_id=sell_asset_id,
            sell_asset_with_amount_asset=sell_asset_json,
            sell_asset_with_amount_amount=sell_amount,
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
