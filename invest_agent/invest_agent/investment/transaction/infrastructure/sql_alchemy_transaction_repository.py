from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)

Base = declarative_base()


class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    sell_balance = Column(Text)
    buy_balance = Column(Text)
    type = Column(String)
    created_at = Column(Integer)
    transaction_hash = Column(String)
    order_id = Column(String)
    trigger = Column(String)
    fees = Column(String)
    basket_id = Column(String, nullable=True)
    # basket_transaction_id = Column(String, nullable=True)


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                transaction_model = TransactionModel(
                    id=transaction.id,
                    sell_balance=transaction.sell_balance.serialize(),
                    buy_balance=transaction.buy_balance.serialize(),
                    type=transaction.type,
                    created_at=transaction.created_at,
                    transaction_hash=transaction.transaction_hash,
                    order_id=transaction.order_id,
                    trigger=transaction.trigger,
                    fees=transaction.fees,
                    # basket_transaction_id=transaction.basket_transaction_id,
                )
                session.add(transaction_model)
        return transaction
