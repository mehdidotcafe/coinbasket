from dataclasses import dataclass

from api.chain.balance import Balance
from api.investment.exchange.exchange import SignableTransaction


@dataclass
class SignedInvestmentPlanStep:
    buy_balance: Balance
    sell_balance: Balance
    transactions: list[SignableTransaction]
    signatures: list[str]
