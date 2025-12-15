from api.database.infrastructure.sql_alchemy_base import Base
from api.investment.order.infrastructure.sql_alchemy_order_repository import (
    OrderTryChainTransactionModel,
    OrderTryModel,
    OrderModel,
)
from api.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    TransactionModel,
)
from api.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    PostingModel,
)

models: list[type[Base]] = [
    OrderTryChainTransactionModel,
    OrderTryModel,
    OrderModel,
    TransactionModel,
    PostingModel,
]
