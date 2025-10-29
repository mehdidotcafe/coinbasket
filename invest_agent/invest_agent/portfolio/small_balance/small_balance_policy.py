# @Copilot

from abc import ABC, abstractmethod

from invest_agent.chain.balance import BalanceAtomic


class SmallBalancePolicy(ABC):
    @abstractmethod
    def is_small_balance(
        self, balance: BalanceAtomic, usd_rate_balance: BalanceAtomic
    ) -> bool:
        raise NotImplementedError
