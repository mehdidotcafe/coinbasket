from dataclasses import dataclass

from api.chain.balance import Balance


@dataclass
class ConfirmedOrder:
    buy_balance: Balance
    sell_balance: Balance
