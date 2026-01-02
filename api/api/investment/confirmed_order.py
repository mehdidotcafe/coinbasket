from dataclasses import dataclass

# from api.address.address import Address
from api.chain.balance import Balance

ConfirmedOrderId = str


@dataclass
class ConfirmedOrder:
    # id: ConfirmedOrderId
    # address: Address
    buy_balance: Balance
    sell_balance: Balance
