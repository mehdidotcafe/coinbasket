from dataclasses import dataclass

from api.address.address import Address
from api.chain.balance import Balance
from api.investment.planned_order import PlannedOrderId

ConfirmedOrderId = str


@dataclass
class ConfirmedOrder:
    id: ConfirmedOrderId
    planned_order_id: PlannedOrderId
    address: Address
    buy_balance: Balance
    sell_balance: Balance
