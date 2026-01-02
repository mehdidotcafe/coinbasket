from typing import Any
from api.address.address import Address
from api.investment.signable_order import SignableOrder
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
from sqlalchemy.dialects.postgresql import NUMERIC, JSONB
from api.chain.balance import BalanceAtomic
from api.investment.order.signable_order_repository import SignableOrderRepository
from api.investment.exchange.exchange import SignableTransaction
from api.chain.chain import Gas


class SignableOrderModel(Base):
    __tablename__ = "signable_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    confirmed_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("confirmed_orders.id")
    )
    address: Mapped[str] = mapped_column(String(42))

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[str] = mapped_column()
    buy_balance_amount: Mapped[str] = mapped_column()
    buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    buy_balance_decimals: Mapped[int] = mapped_column()

    sell_balance_asset_id: Mapped[str] = mapped_column(String())
    sell_balance_asset: Mapped[str] = mapped_column()
    sell_balance_amount: Mapped[str] = mapped_column()
    sell_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    sell_balance_decimals: Mapped[int] = mapped_column()

    signature_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    transaction: Mapped[dict[str, Any]] = mapped_column(JSONB)

    def to_domain(self) -> SignableOrder:
        return SignableOrder(
            id=self.id,
            confirmed_order_id=self.confirmed_order_id,
            address=Address(self.address),
            buy_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.buy_balance_asset),
                amount=Decimal(self.buy_balance_amount),
                amount_atomic=int(self.buy_balance_amount_atomic),
                decimals=self.buy_balance_decimals,
            ),
            sell_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.sell_balance_asset),
                amount=Decimal(self.sell_balance_amount),
                amount_atomic=int(self.sell_balance_amount_atomic),
                decimals=self.sell_balance_decimals,
            ),
            signature_payload=self.signature_payload,
            transaction=SignableTransaction(
                type=self.transaction["type"],
                amount=self.transaction["amount"],
                data=self.transaction["data"],
                gas=Gas(
                    gas=self.transaction["gas"]["gas"],
                    gas_price=self.transaction["gas"]["gas_price"],
                )
                if self.transaction.get("gas")
                else None,
                to_address=self.transaction.get("to_address"),
            ),
        )

    @staticmethod
    def from_domain(signable_order: SignableOrder) -> "SignableOrderModel":
        return SignableOrderModel(
            id=signable_order.id,
            confirmed_order_id=signable_order.confirmed_order_id,
            address=str(signable_order.address),
            buy_balance_asset_id=signable_order.buy_balance.asset.id,
            buy_balance_asset=json.dumps(signable_order.buy_balance.asset.to_dict()),
            buy_balance_amount=format(signable_order.buy_balance.amount, "f"),
            buy_balance_amount_atomic=signable_order.buy_balance.amount_atomic,
            buy_balance_decimals=signable_order.buy_balance.decimals,
            sell_balance_asset_id=signable_order.sell_balance.asset.id,
            sell_balance_asset=json.dumps(signable_order.sell_balance.asset.to_dict()),
            sell_balance_amount=format(signable_order.sell_balance.amount, "f"),
            sell_balance_amount_atomic=signable_order.sell_balance.amount_atomic,
            sell_balance_decimals=signable_order.sell_balance.decimals,
            signature_payload=signable_order.signature_payload,
            transaction=signable_order.transaction.to_dict(),
        )


class SqlAlchemySignableOrderRepository(
    SignableOrderRepository, SqlAlchemyBaseRepository
):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def save(
        self, signable_order: SignableOrder, session: NullableSession = None
    ) -> SignableOrder:
        async with self.get_session(session) as session:
            session.add(SignableOrderModel.from_domain(signable_order))
        return signable_order
