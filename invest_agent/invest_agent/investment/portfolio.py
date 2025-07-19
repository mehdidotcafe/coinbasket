from dataclasses import dataclass
from invest_agent.investment.order.order import Order
from invest_agent.investment.transaction.transaction import Transaction


@dataclass
class Portfolio:
    transactions: list[Transaction]
    orders: list[Order]
