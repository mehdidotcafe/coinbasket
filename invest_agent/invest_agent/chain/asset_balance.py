from dataclasses import dataclass

from decimal import Decimal
from invest_agent.chain.balance import Balance
from protocol.basket import Basket


@dataclass
class TokenBalance:
    buy_balance: Balance
    sell_balance: Balance


@dataclass
class BasketBalance:
    basket: Basket
    amount: Decimal


AssetBalance = Balance | BasketBalance
