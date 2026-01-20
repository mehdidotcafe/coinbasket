# @Copilot

from decimal import Decimal
from typing import TypedDict
from api.chain.balance import BalanceAtomic
from api.portfolio.small_balance.small_balance_policy import (
    SmallBalancePolicy,
)


class Configuration(TypedDict):
    threshold: Decimal


class AbsoluteSmallBalancePolicy(SmallBalancePolicy):
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def is_small_balance(
        self, balance: BalanceAtomic, usd_rate_balance: BalanceAtomic
    ) -> bool:
        usd_balance_amount = usd_rate_balance.amount * balance.amount
        return usd_balance_amount < self.configuration["threshold"]
