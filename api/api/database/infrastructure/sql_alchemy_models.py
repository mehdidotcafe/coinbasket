from api.database.infrastructure.sql_alchemy_base import Base
from api.investment.order.infrastructure.sql_alchemy_confirmed_order_repository import (
    ConfirmedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_executed_order_repository import (
    ExecutedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_intended_order_repository import (
    IntendedOrderModel,
)

from api.investment.order.infrastructure.sql_alchemy_planned_order_repository import (
    PlannedOrderModel,
)
from api.investment.order.infrastructure.sql_alchemy_signable_order_repository import (
    SignableOrderModel,
)


models: list[type[Base]] = [
    IntendedOrderModel,
    PlannedOrderModel,
    ConfirmedOrderModel,
    SignableOrderModel,
    ExecutedOrderModel,
]
