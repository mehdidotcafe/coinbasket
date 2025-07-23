from dataclasses import dataclass

from decimal import Decimal
from invest_agent.chain.balance import Balance


@dataclass
class TokenBalance:
    buy_balance: Balance
    sell_balance: Balance


@dataclass
class BalancedBasket:
    id: str
    name: str
    description: str
    denomination: Decimal
    balances: list[TokenBalance]


@dataclass
class BasketBalance:
    basket: BalancedBasket
    amount: Decimal


AssetBalance = Balance | BasketBalance
