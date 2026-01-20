from dataclasses import dataclass
from decimal import Decimal

from api.address.address import Address
from api.chain.balance import BalanceAtomic
from api.investment.signable_order import SignableOrderId

ExecutedOrderId = str


@dataclass
class ExecutedOrder:
    id: ExecutedOrderId
    signable_order_id: SignableOrderId
    transaction_hash: str
    address: Address
    buy_balance: BalanceAtomic
    sell_balance: BalanceAtomic
    rate: Decimal | None = None
