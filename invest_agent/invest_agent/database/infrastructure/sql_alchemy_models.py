from invest_agent.database.infrastructure.sql_alchemy_base import Base
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderTryChainTransactionModel,
    OrderTryModel,
    OrderModel,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)

models: list[type[Base]] = [
    OrderTryChainTransactionModel,
    OrderTryModel,
    OrderModel,
    TransactionModel,
]
