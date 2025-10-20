from dataclasses import dataclass

from invest_agent.chain.balance import BalanceAtomic


@dataclass
class Holding:
    balance: BalanceAtomic
    children: list[BalanceAtomic] | None
