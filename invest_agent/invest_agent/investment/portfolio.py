from dataclasses import dataclass
from invest_agent.investment.order import Order
from invest_agent.investment.transaction import Transaction


@dataclass
class Portfolio:
    transactions: list[Transaction]
    orders: list[Order]
