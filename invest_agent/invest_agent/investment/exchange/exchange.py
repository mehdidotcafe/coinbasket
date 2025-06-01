from abc import ABC, abstractmethod
from dataclasses import dataclass

from invest_agent.chain.balance import Balance
from invest_agent.investment.basket_investment import Bid
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_plan import InvestmentPlan
from protocol.token import Token


@dataclass
class ConvertedBalance:
    sell_balance: Balance
    buy_balance: Balance


@dataclass
class Wallet:
    balances: list[ConvertedBalance]
    total_balance: Balance


class Exchange(ABC):
    @abstractmethod
    def execute_investment_plan(
        self,
        investment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:  # noqa: F821
        raise NotImplementedError

    @abstractmethod
    def execute_divestment_plan(
        self,
        divestment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_in_token(
        self, tokens_balance: list[Balance], token: Token
    ) -> Wallet:
        raise NotImplementedError
