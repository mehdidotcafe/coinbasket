from typing import cast
from invest_agent.investment.fees import Fees
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, relationship, Mapped, mapped_column
from invest_agent.chain.balance import Balance
from invest_agent.investment.order.order import (
    ChainTransaction,
    ChainTransactionStatus,
    ChainTransactionType,
    Order,
    OrderStatus,
    OrderTrigger,
    OrderType,
    Try,
    Id,
)
from invest_agent.investment.order.order_repository import OrderRepository


Base = declarative_base()


class OrderTryChainTransactionModel(Base):
    __tablename__ = "order_try_chain_transactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    try_id: Mapped[str] = mapped_column(ForeignKey("order_tries.id"))
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    type: Mapped[str] = mapped_column()
    data: Mapped[str] = mapped_column()
    hash: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()

    try_: Mapped["OrderTryModel"] = relationship(
        "OrderTryModel", back_populates="chain_transactions"
    )


class OrderTryModel(Base):
    __tablename__ = "order_tries"

    id: Mapped[str] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    created_at: Mapped[int] = mapped_column()
    provider: Mapped[str] = mapped_column()
    buy_balance: Mapped[str] = mapped_column()
    fees: Mapped[str | None] = mapped_column(nullable=True)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="tries")
    chain_transactions: Mapped[list[OrderTryChainTransactionModel]] = relationship(
        OrderTryChainTransactionModel, back_populates="try_", lazy="selectin"
    )


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    sell_balance: Mapped[str] = mapped_column()
    buy_balance: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    created_at: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    trigger: Mapped[str] = mapped_column()
    basket_id: Mapped[str | None] = mapped_column(nullable=True)

    # Relationship to OrderTryModel
    tries: Mapped[list[OrderTryModel]] = relationship(
        "OrderTryModel", back_populates="order", lazy="selectin"
    )


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_order(self, order: Order) -> Order:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                stmt = (
                    OrderModel.__table__.insert()
                    .values(
                        id=order.id,
                        sell_balance=order.sell_balance.serialize(),
                        buy_balance=order.buy_balance.serialize(),
                        type=order.type,
                        created_at=order.created_at,
                        status=order.status,
                        trigger=order.trigger,
                        basket_id=order.basket_id,
                    )
                    .prefix_with("OR IGNORE")
                )
                await session.execute(stmt)
        return order

    async def add_order_try(self, order_id: Id, order_try: Try) -> Try:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                try_model = OrderTryModel(
                    id=order_try.id,
                    order_id=order_id,
                    created_at=order_try.created_at,
                    provider=order_try.provider,
                    buy_balance=order_try.buy_balance.serialize(),
                    fees=order_try.fees,
                )
                session.add(try_model)
                for chain_transaction in order_try.chain_transactions:
                    chain_tx_model = OrderTryChainTransactionModel(
                        id=chain_transaction.id,
                        try_id=chain_transaction.try_id,
                        order_id=chain_transaction.order_id,
                        type=chain_transaction.type,
                        data=chain_transaction.data,
                        hash=chain_transaction.hash,
                        status=chain_transaction.status,
                    )
                    session.add(chain_tx_model)
        return order_try

    async def set_order_to_success(self, order_id: Id) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    OrderModel.__table__.update()
                    .where(OrderModel.id == order_id)
                    .values(status="SUCCESS")
                )

    async def set_order_to_failed(self, order_id: Id) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    OrderModel.__table__.update()
                    .where(OrderModel.id == order_id)
                    .values(status="FAILED")
                )

    async def get_pending_orders(self) -> list[Order]:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            stmt = (
                select(OrderModel)
                .options(
                    selectinload(OrderModel.tries).selectinload(
                        OrderTryModel.chain_transactions
                    )
                )
                .where(OrderModel.status == "PENDING")
            )

            result = await session.execute(stmt)
            order_models = result.scalars().all()

            return [
                Order(
                    id=row.id,
                    sell_balance=Balance.deserialize(row.sell_balance),
                    buy_balance=Balance.deserialize(row.buy_balance),
                    type=cast(OrderType, row.type),
                    created_at=row.created_at,
                    status=cast(OrderStatus, row.status),
                    trigger=cast(OrderTrigger, row.trigger),
                    basket_id=row.basket_id,
                    tries=[
                        Try(
                            id=t.id,
                            order_id=t.order_id,
                            created_at=t.created_at,
                            provider=t.provider,
                            buy_balance=Balance.deserialize(t.buy_balance),
                            fees=cast(Fees | None, t.fees),
                            chain_transactions=[
                                ChainTransaction(
                                    id=ct.id,
                                    try_id=ct.try_id,
                                    order_id=ct.order_id,
                                    type=cast(ChainTransactionType, ct.type),
                                    data=ct.data,
                                    hash=ct.hash,
                                    status=cast(ChainTransactionStatus, ct.status),
                                )
                                for ct in t.chain_transactions
                            ],
                        )
                        for t in row.tries
                    ],
                )
                for row in order_models
            ]

    async def set_order_try_chain_transaction_to_success(
        self, chain_transaction_id: Id
    ) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    OrderTryChainTransactionModel.__table__.update()
                    .where(OrderTryChainTransactionModel.id == chain_transaction_id)
                    .values(status="SUCCESS")
                )

    async def set_order_try_chain_transaction_to_fail(
        self, chain_transaction_id: Id
    ) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    OrderTryChainTransactionModel.__table__.update()
                    .where(OrderTryChainTransactionModel.id == chain_transaction_id)
                    .values(status="FAIL")
                )
