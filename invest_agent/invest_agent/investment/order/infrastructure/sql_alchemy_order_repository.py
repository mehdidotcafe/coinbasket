from decimal import Decimal
import json
from typing import TYPE_CHECKING, cast
from invest_agent.database.infrastructure.sql_alchemy_base import Base
from invest_agent.investment.fees import Fees
from protocol.token import Token
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey, String, update
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import insert, NUMERIC
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.order.order import (
    ChainTransaction,
    ChainTransactionStatus,
    ChainTransactionType,
    Order,
    OrderStatus,
    OrderTrigger,
    OrderType,
    OrderAssetType,
    Try,
    Id,
)
from invest_agent.investment.order.order_repository import OrderRepository

if TYPE_CHECKING:
    from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
        TransactionModel,
    )


class OrderTryChainTransactionModel(Base):
    __tablename__ = "order_try_chain_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    try_id: Mapped[str] = mapped_column(String(36), ForeignKey("order_tries.id"))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"))
    type: Mapped[str] = mapped_column()
    data: Mapped[str] = mapped_column()
    hash: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()

    try_: Mapped["OrderTryModel"] = relationship(
        "OrderTryModel", back_populates="chain_transactions"
    )

    def to_domain(self) -> ChainTransaction:
        return ChainTransaction(
            id=self.id,
            try_id=self.try_id,
            order_id=self.order_id,
            type=cast(ChainTransactionType, self.type),
            data=self.data,
            hash=self.hash,
            status=cast(ChainTransactionStatus, self.status),
        )

    @staticmethod
    def from_domain(
        chain_transaction: ChainTransaction,
    ) -> "OrderTryChainTransactionModel":
        return OrderTryChainTransactionModel(
            id=chain_transaction.id,
            try_id=chain_transaction.try_id,
            order_id=chain_transaction.order_id,
            type=chain_transaction.type,
            data=chain_transaction.data,
            hash=chain_transaction.hash,
            status=chain_transaction.status,
        )


class OrderTryModel(Base):
    __tablename__ = "order_tries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "orders.id",
        ),
    )
    created_at: Mapped[int] = mapped_column()
    provider: Mapped[str] = mapped_column()

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[str] = mapped_column()
    buy_balance_amount: Mapped[str] = mapped_column()
    buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    buy_balance_decimals: Mapped[int] = mapped_column()

    fees: Mapped[str | None] = mapped_column(nullable=True)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="tries")
    chain_transactions: Mapped[list[OrderTryChainTransactionModel]] = relationship(
        OrderTryChainTransactionModel,
        back_populates="try_",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> Try:
        return Try(
            id=self.id,
            order_id=self.order_id,
            created_at=self.created_at,
            provider=self.provider,
            buy_balance=BalanceAtomic(
                asset=cast(
                    Token, BalanceAtomic.deserialize_asset(self.buy_balance_asset)
                ),
                amount=Decimal(self.buy_balance_amount),
                amount_atomic=int(self.buy_balance_amount_atomic),
                decimals=self.buy_balance_decimals,
            ),
            fees=Fees.deserialize(self.fees) if self.fees else None,
            chain_transactions=[ct.to_domain() for ct in self.chain_transactions],
        )

    @staticmethod
    def from_domain(try_: Try) -> "OrderTryModel":
        return OrderTryModel(
            id=try_.id,
            order_id=try_.order_id,
            created_at=try_.created_at,
            provider=try_.provider,
            buy_balance_asset_id=try_.buy_balance.asset.id,
            buy_balance_asset=json.dumps(try_.buy_balance.asset.to_dict()),
            buy_balance_amount=format(try_.buy_balance.amount, "f"),
            buy_balance_amount_atomic=try_.buy_balance.amount_atomic,
            buy_balance_decimals=try_.buy_balance.decimals,
            fees=try_.fees.serialize() if try_.fees else None,
            chain_transactions=[
                OrderTryChainTransactionModel.from_domain(ct)
                for ct in try_.chain_transactions
            ],
        )


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    parent_order_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("orders.id", name="fk_orders_parent_order_id_orders_id"),
        nullable=True,
    )

    sell_balance_asset_id: Mapped[str] = mapped_column(String())
    sell_balance_asset: Mapped[str] = mapped_column()
    sell_balance_amount: Mapped[str] = mapped_column()
    sell_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    sell_balance_decimals: Mapped[int] = mapped_column()

    buy_balance_asset_id: Mapped[str] = mapped_column(String())
    buy_balance_asset: Mapped[str] = mapped_column()
    buy_balance_amount: Mapped[str] = mapped_column()
    buy_balance_amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    buy_balance_decimals: Mapped[int] = mapped_column()

    type: Mapped[str] = mapped_column()
    asset_type: Mapped[OrderAssetType] = mapped_column()
    created_at: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    trigger: Mapped[str] = mapped_column()
    basket_id: Mapped[str | None] = mapped_column(String(), nullable=True)

    parent_order: Mapped["OrderModel | None"] = relationship(
        "OrderModel",
        remote_side=[id],
    )

    tries: Mapped[list[OrderTryModel]] = relationship(
        "OrderTryModel",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> Order:
        return Order(
            id=self.id,
            parent_order_id=self.parent_order_id,
            sell_balance=BalanceAtomic(
                asset=cast(
                    Token, BalanceAtomic.deserialize_asset(self.sell_balance_asset)
                ),
                amount=Decimal(self.sell_balance_amount),
                amount_atomic=int(self.sell_balance_amount_atomic),
                decimals=self.sell_balance_decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=cast(
                    Token, BalanceAtomic.deserialize_asset(self.buy_balance_asset)
                ),
                amount=Decimal(self.buy_balance_amount),
                amount_atomic=int(self.buy_balance_amount_atomic),
                decimals=self.buy_balance_decimals,
            ),
            type=cast(OrderType, self.type),
            asset_type=self.asset_type,
            created_at=self.created_at,
            status=cast(OrderStatus, self.status),
            trigger=cast(OrderTrigger, self.trigger),
            basket_id=self.basket_id,
            tries=[t.to_domain() for t in self.tries],
        )

    @staticmethod
    def from_domain(order: Order) -> "OrderModel":
        return OrderModel(
            id=order.id,
            parent_order_id=order.parent_order_id,
            sell_balance_asset_id=order.sell_balance.asset.id,
            sell_balance_asset=json.dumps(order.sell_balance.asset.to_dict()),
            sell_balance_amount=format(order.sell_balance.amount, "f"),
            sell_balance_amount_atomic=order.sell_balance.amount_atomic,
            sell_balance_decimals=order.sell_balance.decimals,
            buy_balance_asset_id=order.buy_balance.asset.id,
            buy_balance_asset=json.dumps(order.buy_balance.asset.to_dict()),
            buy_balance_amount=format(order.buy_balance.amount, "f"),
            buy_balance_amount_atomic=order.buy_balance.amount_atomic,
            buy_balance_decimals=order.buy_balance.decimals,
            type=order.type,
            asset_type=order.asset_type,
            created_at=order.created_at,
            status=order.status,
            trigger=order.trigger,
            basket_id=order.basket_id,
        )


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_order(self, order: Order) -> Order:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                order_model = OrderModel.from_domain(order)

                stmt = (
                    insert(OrderModel)
                    .values(
                        id=order_model.id,
                        parent_order_id=order_model.parent_order_id,
                        sell_balance_asset_id=order_model.sell_balance_asset_id,
                        sell_balance_asset=order_model.sell_balance_asset,
                        sell_balance_amount=order_model.sell_balance_amount,
                        sell_balance_amount_atomic=order_model.sell_balance_amount_atomic,
                        sell_balance_decimals=order_model.sell_balance_decimals,
                        buy_balance_asset_id=order_model.buy_balance_asset_id,
                        buy_balance_asset=order_model.buy_balance_asset,
                        buy_balance_amount=order_model.buy_balance_amount,
                        buy_balance_amount_atomic=order_model.buy_balance_amount_atomic,
                        buy_balance_decimals=order_model.buy_balance_decimals,
                        type=order_model.type,
                        asset_type=order_model.asset_type,
                        created_at=order_model.created_at,
                        status=order_model.status,
                        trigger=order_model.trigger,
                        basket_id=order_model.basket_id,
                    )
                    .on_conflict_do_nothing(index_elements=[OrderModel.id])
                )
                await session.execute(stmt)
        return order

    async def add_order_try(self, order_id: Id, order_try: Try) -> Try:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                session.add(OrderTryModel.from_domain(order_try))
        return order_try

    async def set_order_to_success(self, order_id: Id) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    update(OrderModel)
                    .where(OrderModel.id == order_id)
                    .values(status="SUCCESS")
                    .execution_options(synchronize_session="fetch")
                )

    async def set_order_to_fail(self, order_id: Id) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    update(OrderModel)
                    .where(OrderModel.id == order_id)
                    .values(status="FAIL")
                    .execution_options(synchronize_session="fetch")
                )

    async def get_pending_orders(self) -> list[Order]:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
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

                return [row.to_domain() for row in order_models]

    async def get_orders(
        self, status: OrderStatus | None, limit: int, offset: int
    ) -> list[Order]:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                stmt = select(OrderModel).limit(limit).offset(offset)

                if status:
                    stmt = stmt.where(OrderModel.status == status)

                result = await session.execute(stmt)
                order_models = result.scalars().all()

                return [row.to_domain() for row in order_models]

    async def get_order(self, order_id: Id):
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                stmt = select(OrderModel).where(OrderModel.id == order_id)

                result = await session.execute(stmt)
                order_model = result.scalar()

                return order_model.to_domain() if order_model else None

    async def set_order_try_chain_transaction_to_success(
        self, chain_transaction_id: Id
    ) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    update(OrderTryChainTransactionModel)
                    .where(OrderTryChainTransactionModel.id == chain_transaction_id)
                    .values(status="SUCCESS")
                    .execution_options(synchronize_session="fetch")
                )

    async def set_order_try_chain_transaction_to_fail(
        self, chain_transaction_id: Id
    ) -> None:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                await session.execute(
                    update(OrderTryChainTransactionModel)
                    .where(OrderTryChainTransactionModel.id == chain_transaction_id)
                    .values(status="FAIL")
                    .execution_options(synchronize_session="fetch")
                )
